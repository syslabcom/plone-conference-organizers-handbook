"""Read the repository's CSV/YAML evidence into immutable rendering models."""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final, NewType, NotRequired, TypedDict

import yaml

SourceId = NewType("SourceId", str)
LedgerId = NewType("LedgerId", str)
PAGE_IDS: Final = (
    "conference-index", "conference-data-table", "cost-benchmarks",
    "source-bibliography", "lessons-ledger",
)


@dataclass(frozen=True, slots=True)
class InputError(ValueError):
    detail: str


class JsonSource(TypedDict):
    source_id: str


class SourceBlock(TypedDict):
    files: list[JsonSource]


class ManifestDocument(TypedDict):
    sources: list[JsonSource]
    seattle_2006: SourceBlock
    internal_2026: SourceBlock


class LedgerRow(TypedDict):
    ledger_id: LedgerId
    topic: str
    scope: str
    year: int
    place: str
    org: str
    source_id: SourceId
    text_kind: str
    quote_or_paraphrase: str
    confidence: str
    status: str
    disposition: str
    locator: NotRequired[str]
    issue: NotRequired[str]
    by: NotRequired[str]


class LedgerDocument(TypedDict):
    rows: list[LedgerRow]


class PageRow(TypedDict):
    id: str
    title: str
    kind: str
    path: str


class ChapterDocument(TypedDict):
    entries: list[PageRow]


Thresholds = TypedDict("Thresholds", {"recent-max-age": int, "mid-max-age": int})
Config = TypedDict("Config", {"as-of-year": int, "age-thresholds": Thresholds})


@dataclass(frozen=True, slots=True)
class DocumentParsers:
    manifest: Callable[[str], ManifestDocument] = json.loads
    ledger: Callable[[str], LedgerDocument] = yaml.safe_load
    chapters: Callable[[str], ChapterDocument] = yaml.safe_load
    config: Callable[[str], Config] = yaml.safe_load


PARSERS: Final = DocumentParsers()


@dataclass(frozen=True, slots=True)
class Source:
    id: SourceId
    group: str
    title: str
    url: str
    file: str
    licence: str
    recommendation: str
    reason: str
    archive_note: str = ""

    @property
    def held(self) -> bool:
        return self.recommendation == "exclude-pending-review"


@dataclass(frozen=True, slots=True)
class Lesson:
    ledger_id: LedgerId
    topic: str
    scope: str
    year: int
    place: str
    org: str
    source_id: SourceId
    text_kind: str
    quote_or_paraphrase: str
    confidence: str
    status: str
    disposition: str
    locator: str = ""
    issue: str = ""
    by: str = ""


@dataclass(frozen=True, slots=True)
class Page:
    id: str
    title: str
    kind: str
    path: str


@dataclass(frozen=True, slots=True)
class Evidence:
    root: Path
    sources: tuple[Source, ...]
    lessons: tuple[Lesson, ...]
    pages: tuple[Page, ...]
    as_of: int
    recent: int
    mid: int

    def page(self, page_id: str) -> Page:
        return next(page for page in self.pages if page.id == page_id)

    def placed(self, page_id: str) -> tuple[Lesson, ...]:
        return tuple(row for row in self.lessons if row.disposition == f"placed: {page_id}")


def load(root: Path) -> Evidence:
    """Normalize archive paths and reconcile all three JSON blocks with CSV IDs.

    PyYAML is the repository's declared boundary parser; no extra runtime
    dependencies are introduced for this standalone generator.
    """
    base = root / "data/sources"
    with (base / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    with (base / "archive-audit.csv").open(encoding="utf-8", newline="") as handle:
        audits = {row["source_id"]: row for row in csv.DictReader(handle)}
    document = PARSERS.manifest((base / "manifest.json").read_text(encoding="utf-8"))
    json_rows = [*document["sources"], *document["seattle_2006"]["files"],
                 *document["internal_2026"]["files"]]
    csv_ids = [row["source_id"] for row in manifest]
    if len(csv_ids) != len(set(csv_ids)) or set(csv_ids) != {row["source_id"] for row in json_rows}:
        raise InputError("Manifest CSV IDs must be unique and match the combined JSON blocks")
    sources: list[Source] = []
    for row in sorted(manifest, key=lambda item: item["source_id"]):
        audit = audits.get(row["source_id"], {})
        file = row["file"]
        if not (base / file).is_file() and (base / "bibliography" / file).is_file():
            file = f"bibliography/{file}"
        target = (base / file).resolve()
        if base.resolve() not in target.parents or not target.is_file():
            raise InputError(f"{row['source_id']}: archive path missing or outside data/sources")
        reasons: list[str] = []
        if audit.get("licence_status", "unknown") in {"unknown", "all-rights-reserved-or-unknown"}:
            reasons.append("licence unclear")
        if audit.get("personal_data_flag", "none") != "none":
            reasons.append("personal data")
        if not audit:
            reasons.append("audit row missing")
        sources.append(Source(
            SourceId(row["source_id"]), row["section"], row["title"], row["url"], file,
            audit.get("licence_status", "unknown"),
            audit.get("recommendation", "exclude-pending-review"), "; ".join(reasons),
            audit.get("notes", ""),
        ))
    lesson_rows: list[Lesson] = []
    for path in sorted((root / "data/ledger").glob("*.yml")):
        ledger_document = PARSERS.ledger(path.read_text(encoding="utf-8"))
        lesson_rows.extend(Lesson(**row) for row in ledger_document["rows"])
    lessons = tuple(sorted(lesson_rows, key=lambda row: row.ledger_id))
    if len({row.ledger_id for row in lessons}) != len(lessons):
        raise InputError("Ledger IDs must be unique")
    if any(row.source_id not in set(csv_ids) for row in lessons):
        raise InputError("Ledger cites a source outside the manifest")
    chapter_document = PARSERS.chapters((root / "docs/spec/chapter-list.yml").read_text(encoding="utf-8"))
    entries = chapter_document["entries"]
    pages = tuple(Page(row["id"], row["title"], row["kind"], row["path"]) for row in entries)
    for page_id in PAGE_IDS:
        page = next((page for page in pages if page.id == page_id), None)
        if page is None or not page.path.startswith("docs/evidence/"):
            raise InputError(f"Missing or out-of-scope chapter-list entry: {page_id}")
    config = PARSERS.config((root / "handbook-config.yml").read_text(encoding="utf-8"))
    return Evidence(root, tuple(sources), lessons, pages, config["as-of-year"],
                    config["age-thresholds"]["recent-max-age"], config["age-thresholds"]["mid-max-age"])
