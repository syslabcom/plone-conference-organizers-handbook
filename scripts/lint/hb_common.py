"""Shared repository model for the handbook lint gates.

Loads the root ``handbook-config.yml``, the chapter list, the source manifest,
the requirements register and the ledger files, and defines the fixed
vocabularies of the content contract (docs/spec/).
Every gate receives a ``Repo`` so tests can point it at a fixture tree.
"""

from __future__ import annotations

import csv
import functools
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

# chapter-template.md, section 2.
CHAPTER_HEADINGS: tuple[str, ...] = (
    "Why it matters",
    "Applies when",
    "Decisions you must make",
    "How-to",
    "Principles and general lessons",
    "Case notes",
    "Risks",
    "Thin content",
    "Sources and further reading",
)
# chapter-template.md, section 6.2.
PLAYBOOK_HEADINGS: tuple[str, ...] = (
    "Triggers",
    "First-hour actions",
    "Owner roles",
    "Related chapters",
)

KINDS = frozenset({"chapter", "page", "playbook", "annex", "appendix", "generated"})
STATUSES = frozenset({"planned", "written"})
PARTS = frozenset({"0", "1", "2", "3", "4", "5", "appendices"})
ENTRY_KEYS = ("id", "title", "part", "workstream", "kind", "path", "status")
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")

REGISTER_STATUSES = frozenset(
    {"verified-current", "verified-changed", "unverifiable", "unverified-pending-Foundation-ask"}
)
MUST_STATUSES = frozenset({"verified-current", "verified-changed"})
CONFIDENCE_ORDER: dict[str, int] = {"observed": 0, "reported": 1, "hearsay": 2}

# conventions.md, section 3.5.
CONTEXT_VALUES: dict[str, frozenset[str] | None] = {
    "size": frozenset({"small", "medium", "large"}),
    "jurisdiction": None,  # ISO 3166-1 alpha-2 or EU, checked by pattern
    "organizer": frozenset({"company", "volunteer-group", "foundation-led", "mixed"}),
    "budget": frozenset({"seed-loan", "financial-agent", "own-risk"}),
    "venue": frozenset({"hotel", "university", "conference-center", "mixed"}),
    "format": frozenset({"in-person", "hybrid", "online"}),
    "language": None,  # ISO 639-1, checked by pattern
}
ISO_COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
ISO_LANGUAGE_RE = re.compile(r"^[a-z]{2}$")
ISO_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
ISSUE_RE = re.compile(r"^(#[0-9]+|https://github\.com/[^/\s]+/[^/\s]+/issues/[0-9]+)$")


@dataclass(frozen=True, slots=True)
class Finding:
    """One lint failure, addressed by stable rule code."""

    code: str
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code} {self.message}"


@dataclass(frozen=True, slots=True)
class Entry:
    """One chapter-list entry."""

    id: str
    title: str
    part: str
    workstream: str
    kind: str
    path: str
    status: str

    @property
    def written(self) -> bool:
        return self.status == "written"


def slugify(text: str) -> str:
    """Lowercase, non-alphanumeric runs become single hyphens (chapter-template.md, section 2)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


CHAPTER_SLUGS: tuple[str, ...] = tuple(slugify(h) for h in CHAPTER_HEADINGS)
PLAYBOOK_SLUGS: tuple[str, ...] = tuple(slugify(h) for h in PLAYBOOK_HEADINGS)


def slugs_for_kind(kind: str) -> tuple[str, ...]:
    """The valid anchor slugs for a page kind; empty for kinds that take no anchor."""
    match kind:
        case "chapter":
            return CHAPTER_SLUGS
        case "playbook":
            return PLAYBOOK_SLUGS
        case _:
            return ()


def search_regex(pattern: str) -> re.Pattern[str]:
    """Turn an anchored config pattern (``^S[0-9]{3}$``) into a token search regex."""
    core = pattern.removeprefix("^").removesuffix("$")
    return re.compile(rf"(?<![A-Za-z0-9-]){core}(?![A-Za-z0-9])")


def rel(repo: Repo, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def validate_context_token(token: str, *, allow_bare: bool) -> str | None:
    """Return an error message for an invalid context token, or None."""
    dim, sep, values = token.partition("=")
    if dim not in CONTEXT_VALUES:
        return f"unknown context dimension {dim!r}"
    if not sep:
        return None if allow_bare else f"context token {token!r} needs values"
    items = [v.strip() for v in values.split(",")]
    if any(not v for v in items):
        return f"empty value in {token!r}"
    if len(set(items)) != len(items):
        return f"duplicate value in {token!r}"
    allowed = CONTEXT_VALUES[dim]
    for value in items:
        match dim:
            case "jurisdiction":
                ok = value == "EU" or bool(ISO_COUNTRY_RE.match(value))
            case "language":
                ok = bool(ISO_LANGUAGE_RE.match(value))
            case _:
                ok = allowed is not None and value in allowed
        if not ok:
            return f"invalid value {value!r} for {dim}"
    return None


def parse_context(text: str) -> dict[str, frozenset[str]]:
    """Parse ``size=small; jurisdiction=NL,BE`` into dimension -> value set."""
    result: dict[str, frozenset[str]] = {}
    for token in text.split(";"):
        dim, _, values = token.strip().partition("=")
        result[dim] = frozenset(v.strip() for v in values.split(","))
    return result


def contexts_distinguish(a: str | None, b: str | None) -> bool:
    """Two contexts distinguish when a shared dimension has disjoint values (conventions.md 3.5)."""
    if not a or not b:
        return False
    ca, cb = parse_context(a), parse_context(b)
    return any(dim in cb and not (ca[dim] & cb[dim]) for dim in ca)


class Repo:
    """A handbook tree: the real repository or a test fixture."""

    def __init__(self, root: Path) -> None:
        self.root: Path = root

    def path(self, relative: str) -> Path:
        return self.root / relative

    @functools.cached_property
    def config(self) -> dict[str, Any]:
        with self.path("handbook-config.yml").open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise ValueError("handbook-config.yml is not a mapping")
        return data

    def config_path(self, key: str) -> Path:
        return self.path(self.config["paths"][key])

    def pattern(self, key: str) -> re.Pattern[str]:
        return re.compile(self.config[key])

    def token_regex(self, key: str) -> re.Pattern[str]:
        return search_regex(self.config[key])

    @functools.cached_property
    def raw_chapter_list(self) -> list[Any]:
        with self.config_path("chapter-list").open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        entries = data.get("entries") if isinstance(data, dict) else None
        return entries if isinstance(entries, list) else []

    @functools.cached_property
    def entries(self) -> tuple[Entry, ...]:
        result: list[Entry] = []
        for raw in self.raw_chapter_list:
            if isinstance(raw, dict) and all(isinstance(raw.get(k), str) for k in ENTRY_KEYS):
                result.append(Entry(**{k: raw[k] for k in ENTRY_KEYS}))
        return tuple(result)

    @functools.cached_property
    def entries_by_id(self) -> dict[str, Entry]:
        return {entry.id: entry for entry in self.entries}

    @functools.cached_property
    def entries_by_path(self) -> dict[str, Entry]:
        return {entry.path: entry for entry in self.entries}

    def written_entries(self) -> list[Entry]:
        return [e for e in self.entries if e.written]

    @functools.cached_property
    def manifest_rows(self) -> list[dict[str, str]]:
        path = self.config_path("source-manifest")
        if not path.is_file():
            return []
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    @functools.cached_property
    def manifest(self) -> dict[str, dict[str, str]]:
        return {row["source_id"]: row for row in self.manifest_rows if row.get("source_id")}

    @functools.cached_property
    def register(self) -> dict[str, dict[str, Any]]:
        path = self.config_path("requirements-register")
        if not path.is_file():
            return {}
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        rows = data.get("rows", []) if isinstance(data, dict) else []
        return {str(r["id"]): r for r in rows if isinstance(r, dict) and "id" in r}

    @functools.cached_property
    def ledger_files(self) -> list[Path]:
        return sorted(self.root.glob(self.config["paths"]["ledger-glob"]))

    @functools.cached_property
    def ledger_docs(self) -> list[tuple[Path, Any, str | None]]:
        """Every ledger file as (path, parsed data or None, YAML error or None)."""
        docs: list[tuple[Path, Any, str | None]] = []
        for path in self.ledger_files:
            try:
                with path.open(encoding="utf-8") as handle:
                    docs.append((path, yaml.safe_load(handle), None))
            except yaml.YAMLError as error:
                docs.append((path, None, str(error)))
        return docs

    @functools.cached_property
    def ledger_rows(self) -> dict[str, dict[str, Any]]:
        """Rows by ledger_id; the first occurrence wins (G7 reports duplicates)."""
        rows: dict[str, dict[str, Any]] = {}
        for _path, data, _error in self.ledger_docs:
            if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
                continue
            for row in data["rows"]:
                if isinstance(row, dict) and isinstance(row.get("ledger_id"), str):
                    rows.setdefault(row["ledger_id"], row)
        return rows

    def markdown_pages(self, *, include_spec: bool = False) -> list[Path]:
        pages = sorted(self.path("docs").rglob("*.md"))
        if include_spec:
            return pages
        spec = self.path("docs/spec")
        return [p for p in pages if spec not in p.parents]


def report(findings: Sequence[Finding], gate: str) -> int:
    """Print findings and return the process exit code."""
    for finding in findings:
        print(finding)
    status = "FAIL" if findings else "OK"
    print(f"{gate}: {status} ({len(findings)} finding(s))", file=sys.stderr)
    return 1 if findings else 0


def codes(findings: Iterable[Finding]) -> set[str]:
    return {f.code for f in findings}
