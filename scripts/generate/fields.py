"""Independent implementation of conventions.md sections 2.2, 3.2, 4.2 and 7.2."""

import re
from datetime import date
from types import MappingProxyType
from typing import Final, assert_never

from .models import DEFAULT_CONFIG, Config, ConventionError, Fields, Kind

AREAS: Final = (
    "hybrid-online", "accessibility", "non-eu-legal-tax-visa",
    "sponsorship-down-market", "pricing-elasticity", "small-budget",
    "health-safety", "sustainability", "jurisdiction-annexes", "post-mortem-2026",
)
ISSUE: Final = r"(?:#[0-9]+|https://github\.com/[^/\s]+/[^/\s]+/issues/[0-9]+)"
REQUIRED: Final = {
    "lesson": {"scope", "source", "ledger", "confidence", "status"},
    "thin": {"kind", "needs", "who-might-know"},
    "risk": {"likelihood", "impact", "mitigation"},
}
ALLOWED: Final = {
    "lesson": REQUIRED["lesson"] | {"year", "place", "org", "basis", "reason", "context", "issue", "by", "conflicts-with"},
    "thin": REQUIRED["thin"] | {"area", "issue", "since"},
    "risk": REQUIRED["risk"] | {"owner-role", "playbook"},
}


def parse_field_line(line: str, config: Config = DEFAULT_CONFIG, implied_kind: Kind | None = None) -> Fields:
    """Parse exactly one physical field line; reject unknown, empty and repeated keys."""
    if "\n" in line.strip() or "\r" in line.strip():
        raise ConventionError("B01", "field lines cannot wrap")
    parts = line.strip().split(" | ")
    kind: Kind
    match parts[0]:
        case "lesson" | "thin" | "risk" as parsed:
            kind = parsed
        case _:
            raise ConventionError("B01", "unknown block kind")
    if implied_kind is not None and kind != implied_kind:
        raise ConventionError("B02", "field kind differs from class-implied kind")
    fields: dict[str, str] = {}
    for part in parts[1:]:
        key, separator, value = part.partition(":")
        key, value = key.strip(), value.strip()
        if not separator or not re.fullmatch(r"[a-z][a-z-]*", key) or not value:
            raise ConventionError("B02", f"invalid field segment: {part!r}")
        if key in fields or key not in ALLOWED[kind]:
            raise ConventionError("B02", f"duplicate or unknown key: {key}")
        fields[key] = value
    missing = REQUIRED[kind] - fields.keys()
    if missing:
        raise ConventionError({"lesson": "L01", "thin": "T01", "risk": "R01"}[kind], f"missing fields: {', '.join(sorted(missing))}")
    result = Fields(kind, MappingProxyType(fields))
    match kind:
        case "lesson":
            validate_lesson(result, config)
        case "thin":
            if fields["kind"] not in {"gap", "single-source", "stale"}:
                raise ConventionError("T01", "invalid thin kind")
            if "area" in fields and fields["area"] not in (*AREAS, "other"):
                raise ConventionError("T01", "invalid thin area")
            if "since" in fields:
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", fields["since"]):
                    raise ConventionError("T01", "since must be an ISO date")
                try:
                    _ = date.fromisoformat(fields["since"])
                except ValueError as error:
                    raise ConventionError("T01", "invalid since date") from error
        case "risk":
            if fields["likelihood"] not in {"low", "medium", "high"} or fields["impact"] not in {"low", "medium", "high"}:
                raise ConventionError("R01", "invalid risk likelihood or impact")
            if len(fields["mitigation"]) > 300:
                raise ConventionError("R01", "mitigation exceeds 300 characters")
        case _:
            assert_never(kind)
    if "issue" in fields and not re.fullmatch(ISSUE, fields["issue"]):
        raise ConventionError("L07" if kind == "lesson" else "T01", "invalid issue reference")
    return result


def validate_lesson(fields: Fields, config: Config) -> None:
    """Enforce scope-dependent field presence and values before computing any badge."""
    f = fields.values
    match f["scope"]:
        case "specific":
            if not {"year", "place", "org"} <= f.keys() or {"basis", "reason"} & f.keys():
                raise ConventionError("L01", "specific requires year, place, org; forbids basis and reason")
            if not re.fullmatch(r"[0-9]+", f["year"]) or int(f["year"]) < 2000:
                raise ConventionError("L01", "year must be an integer from 2000")
            if int(f["year"]) > config.as_of_year:
                raise ConventionError("L02", "year exceeds as-of-year")
            if len(f["place"]) > 40 or len(f["org"]) > 60:
                raise ConventionError("L01", "place or org exceeds its character limit")
        case "general":
            if {"year", "place", "org"} & f.keys() or "basis" not in f:
                raise ConventionError("L01", "general requires basis; forbids year, place and org")
            match f["basis"]:
                case "structural":
                    if "reason" not in f or len(f["reason"]) > 200:
                        raise ConventionError("L01", "structural basis requires a reason of at most 200 characters")
                case "independent-conferences":
                    if "reason" in f:
                        raise ConventionError("L01", "reason is only allowed for structural basis")
                case _:
                    raise ConventionError("L01", "invalid general basis")
        case _:
            raise ConventionError("L01", "invalid lesson scope")
    if f["confidence"] not in {"observed", "reported", "hearsay"} or f["status"] not in {"active", "contested", "superseded"}:
        raise ConventionError("L01", "invalid confidence or status")
    for status, key in (("contested", "issue"), ("superseded", "by")):
        if (f["status"] == status) != (key in f):
            raise ConventionError("L07", f"{key} is required only for {status}")
    for key, pattern in (("source", config.source_pattern), ("ledger", config.ledger_pattern), ("conflicts-with", config.ledger_pattern), ("by", config.ledger_pattern)):
        if key in f:
            items = [item.strip() for item in f[key].split(",")]
            if any(not re.fullmatch(pattern, item) for item in items) or (key == "by" and len(items) != 1):
                raise ConventionError("L01", f"invalid {key} IDs")
    if "context" in f:
        validate_context(f["context"])


def validate_context(context: str) -> None:
    vocab = {
        "size": {"small", "medium", "large"},
        "organizer": {"company", "volunteer-group", "foundation-led", "mixed"},
        "budget": {"seed-loan", "financial-agent", "own-risk"},
        "venue": {"hotel", "university", "conference-center", "mixed"},
        "format": {"in-person", "hybrid", "online"},
    }
    seen: set[str] = set()
    for token in context.split("; "):
        dimension, separator, values = token.partition("=")
        items = values.split(",")
        if not separator or dimension in seen or not all(items):
            raise ConventionError("L01", "invalid context token")
        seen.add(dimension)
        match dimension:
            case "jurisdiction":
                valid = all(re.fullmatch(r"[A-Z]{2}", item) for item in items)
            case "language":
                valid = all(re.fullmatch(r"[a-z]{2}", item) for item in items)
            case _:
                valid = dimension in vocab and set(items) <= vocab[dimension]
        if not valid:
            raise ConventionError("L01", "invalid context dimension or value")
