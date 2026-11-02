"""Front-matter validation, rules F01 to F09 (front-matter.md, section 4).

Used by the chapter contract (G4) and the freshness report (G10).
"""

from __future__ import annotations

import calendar
import datetime as dt
import re
from typing import Any

import yaml

from g3_temporal import undated_temporal_words
from hb_common import ISO_COUNTRY_RE, Entry, Repo, validate_context_token

ALL_KEYS = frozenset({"steward", "deputy", "review-by", "maturity", "applies-to", "diataxis", "myst", "jurisdiction"})
OWNERSHIP_KEYS = ("steward", "deputy", "review-by", "maturity", "applies-to")
MATURITIES = ("stub", "draft", "reviewed", "proven")
DIATAXIS = frozenset({"tutorial", "how-to", "reference", "explanation", "experience-report", "mixed"})
FIXED_DIATAXIS = {"chapter": "mixed", "playbook": "how-to", "generated": "reference"}
HANDLE_RE = re.compile(r"^@[A-Za-z0-9][A-Za-z0-9-]{0,38}(/[A-Za-z0-9._-]+)?$")
JURISDICTION_DIR = "docs/annexes/jurisdictions/"
DESCRIPTION_KEY = "description lang=en"


def add_months(day: dt.date, months: int) -> dt.date:
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    return dt.date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def as_date(value: Any) -> dt.date | None:
    """Accept a YAML date or an ISO string (front-matter.md, section 1)."""
    if isinstance(value, dt.datetime):
        return None
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def load(text: str | None) -> tuple[dict[str, Any] | None, str | None]:
    """Parse the front-matter text into a mapping, or return an F01 message."""
    if text is None:
        return None, "front matter block is missing"
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        return None, f"front matter is not valid YAML: {error}"
    if not isinstance(data, dict):
        return None, "front matter is not a mapping"
    return data, None


def _valid_owner(value: Any) -> bool:
    return value == "unassigned" or (isinstance(value, str) and bool(HANDLE_RE.match(value)))


def check(
    repo: Repo, entry: Entry, fm: dict[str, Any], as_of: dt.date
) -> list[tuple[str, str]]:
    """Return (code, message) pairs for one parsed front-matter mapping."""
    errors: list[tuple[str, str]] = []
    unknown = sorted(set(fm) - ALL_KEYS)
    if unknown:
        errors.append(("F01", f"keys not allowed: {', '.join(map(str, unknown))}"))

    generated = entry.kind == "generated"
    required = {"diataxis", "myst"} | (set() if generated else set(OWNERSHIP_KEYS))
    missing = sorted(required - set(fm))
    if missing:
        errors.append(("F02", f"missing required keys for kind {entry.kind}: {', '.join(missing)}"))
    if generated:
        forbidden = sorted(set(fm) & set(OWNERSHIP_KEYS))
        if forbidden:
            errors.append(("F02", f"keys forbidden on generated pages: {', '.join(forbidden)}"))

    if not generated:
        errors.extend(_check_ownership(repo, entry, fm, as_of))
    errors.extend(_check_diataxis(entry, fm))
    errors.extend(_check_myst(fm))
    errors.extend(_check_jurisdiction(entry, fm))
    return errors


def _check_ownership(repo: Repo, entry: Entry, fm: dict[str, Any], as_of: dt.date) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    steward, deputy, maturity = fm.get("steward"), fm.get("deputy"), fm.get("maturity")
    if "steward" in fm and not _valid_owner(steward):
        errors.append(("F03", f"steward {steward!r} is not 'unassigned' or a GitHub handle"))
    if "deputy" in fm and not _valid_owner(deputy):
        errors.append(("F03", f"deputy {deputy!r} is not 'unassigned' or a GitHub handle"))
    if steward == deputy and steward != "unassigned" and "steward" in fm:
        errors.append(("F03", "steward and deputy must differ"))
    if maturity in ("reviewed", "proven") and steward == "unassigned":
        errors.append(("F03", f"maturity {maturity} requires a named steward"))

    if "review-by" in fm:
        review_by = as_date(fm["review-by"])
        if review_by is None:
            errors.append(("F04", f"review-by {fm['review-by']!r} is not a valid ISO date"))
        else:
            fast = repo.config["fast-aging"]
            fast_aging = entry.id in fast.get("ids", []) or entry.kind in fast.get("kinds", [])
            months = fast["max-months"] if fast_aging else repo.config["max-review-months"]
            horizon = add_months(as_of, int(months))
            if review_by > horizon:
                errors.append(("F04", f"review-by {review_by} is later than {horizon} ({months} months after {as_of})"))

    if "maturity" in fm and maturity not in MATURITIES:
        errors.append(("F05", f"maturity {maturity!r} is not one of {', '.join(MATURITIES)}"))

    if "applies-to" in fm:
        errors.extend(("F06", m) for m in applies_to_errors(fm["applies-to"]))
    return errors


def applies_to_errors(value: Any) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
        return ["applies-to must be a non-empty list of strings"]
    errors: list[str] = []
    if "all" in value and len(value) != 1:
        errors.append("'all' must be the only applies-to item")
    if len(set(value)) != len(value):
        errors.append("applies-to items must be unique")
    for item in value:
        if item == "all":
            continue
        message = validate_context_token(item, allow_bare=True)
        if message:
            errors.append(message)
    dims = [item.partition("=")[0] for item in value]
    if len(set(dims)) != len(dims):
        errors.append("a dimension appears in more than one applies-to item")
    return errors


def _check_diataxis(entry: Entry, fm: dict[str, Any]) -> list[tuple[str, str]]:
    if "diataxis" not in fm:
        return []
    value = fm["diataxis"]
    if value not in DIATAXIS:
        return [("F07", f"diataxis {value!r} is not allowed")]
    fixed = FIXED_DIATAXIS.get(entry.kind)
    if fixed and value != fixed:
        return [("F07", f"kind {entry.kind} requires diataxis {fixed}, found {value}")]
    return []


def _check_myst(fm: dict[str, Any]) -> list[tuple[str, str]]:
    if "myst" not in fm:
        return []
    myst = fm["myst"]
    if not isinstance(myst, dict) or set(myst) != {"html_meta"} or not isinstance(myst["html_meta"], dict):
        return [("F08", "myst must be a mapping with exactly one key, html_meta")]
    meta: dict[str, Any] = myst["html_meta"]
    errors: list[tuple[str, str]] = []
    description = meta.get(DESCRIPTION_KEY)
    if not isinstance(description, str):
        errors.append(("F08", f"html_meta needs {DESCRIPTION_KEY!r}"))
    else:
        if "\n" in description or not 50 <= len(description) <= 160:
            errors.append(("F08", f"description must be one line of 50 to 160 characters (has {len(description)})"))
        if not description.rstrip().endswith("."):
            errors.append(("F08", "description must be a plain sentence ending with a period"))
        words = undated_temporal_words(description)
        if words:
            errors.append(("F08", f"description uses temporal words without a date: {', '.join(words)}"))
    keywords = meta.get("keywords")
    if not isinstance(keywords, str):
        errors.append(("F08", "html_meta needs 'keywords'"))
    else:
        items = [k.strip() for k in keywords.split(",")]
        if len(items) < 3 or any(not k for k in items) or items[0] != "Plone":
            errors.append(("F08", "keywords need at least three comma-separated items, the first being 'Plone'"))
    return errors


def _check_jurisdiction(entry: Entry, fm: dict[str, Any]) -> list[tuple[str, str]]:
    expected = entry.kind == "annex" and entry.path.startswith(JURISDICTION_DIR)
    present = "jurisdiction" in fm
    if expected and not present:
        return [("F09", "jurisdiction annexes need a jurisdiction field")]
    if present and not expected:
        return [("F09", "jurisdiction is only allowed on annexes under docs/annexes/jurisdictions/")]
    if present and not (isinstance(fm["jurisdiction"], str) and ISO_COUNTRY_RE.match(fm["jurisdiction"])):
        return [("F09", f"jurisdiction {fm['jurisdiction']!r} is not an uppercase ISO 3166-1 alpha-2 code")]
    return []
