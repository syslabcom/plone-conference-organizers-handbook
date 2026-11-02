"""Gate G5: convention validation (conventions.md, section 9).

Validates the managed lesson, thin and risk blocks and the MUST, DEFAULT and
OPTION badges on every written page, with the rule codes B01-B06, L01-L10,
T01-T02, R01-R04 and N01-N04.

Usage: venv/bin/python scripts/lint/g5_conventions.py [--root PATH]
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import hb_badges
from hb_common import (
    CONFIDENCE_ORDER,
    ISO_DATE_RE,
    ISSUE_RE,
    REPO_ROOT,
    Entry,
    Finding,
    Repo,
    contexts_distinguish,
    rel,
    report,
    slugify,
    validate_context_token,
)
from hb_frontmatter import load as load_front_matter
from hb_ledger import anchor_error, parse_disposition
from hb_markdown import Block, BlockKind, Page, colon_managed_fences, content_lines, parse_page, split_list

LESSON_KEYS = frozenset(
    {"scope", "year", "place", "org", "source", "ledger", "confidence", "status",
     "basis", "reason", "context", "issue", "by", "conflicts-with"}
)
THIN_KEYS = frozenset({"kind", "needs", "who-might-know", "area", "issue", "since"})
RISK_KEYS = frozenset({"likelihood", "impact", "mitigation", "owner-role", "playbook"})
KEYS_BY_KIND = {"lesson": LESSON_KEYS, "thin": THIN_KEYS, "risk": RISK_KEYS}
DIRECTIVE_BY_KIND = {"lesson": "note", "thin": "warning", "risk": "warning"}
THIN_KINDS = frozenset({"gap", "single-source", "stale"})
THIN_AREAS = frozenset(
    {"hybrid-online", "accessibility", "non-eu-legal-tax-visa", "sponsorship-down-market",
     "pricing-elasticity", "small-budget", "health-safety", "sustainability",
     "jurisdiction-annexes", "post-mortem-2026", "other"}
)
LEVELS = frozenset({"low", "medium", "high"})
SEC_PRINCIPLES, SEC_CASES, SEC_RISKS, SEC_THIN = (
    "Principles and general lessons", "Case notes", "Risks", "Thin content",
)
NONE_KNOWN_PREFIX = "None known as of "
NO_RISKS_PREFIX = "No chapter-specific risks recorded. Rationale: "


@dataclass(slots=True)
class Lesson:
    entry: Entry
    path: str
    block: Block
    fields: dict[str, str]
    valid: bool

    @property
    def ledger_ids(self) -> list[str]:
        return split_list(self.fields.get("ledger", ""))


def age_bucket(age: int, recent_max: int, mid_max: int) -> str:
    if age <= recent_max:
        return "recent"
    if age <= mid_max:
        return "mid"
    return "old"


def lesson_title(f: dict[str, str], as_of_year: int, recent_max: int, mid_max: int) -> str:
    """conventions.md, section 3.3."""
    if f["scope"] == "general":
        base, suffixes = "[general]", []
    else:
        age = as_of_year - int(f["year"])
        base = f"[specific \u00b7 {f['year']} \u00b7 {f['place']} \u00b7 {age} y]"
        suffixes = ["stale-prone"] if age_bucket(age, recent_max, mid_max) == "old" else []
    if f["status"] != "active":
        suffixes.append(f["status"])
    return " ".join([base, *suffixes])


def lesson_classes(f: dict[str, str], as_of_year: int, recent_max: int, mid_max: int) -> set[str]:
    """conventions.md, section 3.3."""
    classes = {"hb-lesson", f"hb-{f['scope']}"}
    if f["scope"] == "specific":
        bucket = age_bucket(as_of_year - int(f["year"]), recent_max, mid_max)
        classes.add(f"hb-age-{bucket}")
        if bucket == "old":
            classes.add("hb-stale-prone")
    if f["status"] != "active":
        classes.add(f"hb-{f['status']}")
    return classes


class PageChecker:
    """All per-page G5 rules for one written page."""

    def __init__(self, repo: Repo, entry: Entry, page: Page) -> None:
        self.repo: Repo = repo
        self.entry: Entry = entry
        self.page: Page = page
        self.path: str = rel(repo, page.path)
        self.findings: list[Finding] = []
        self.lessons: list[Lesson] = []
        cfg = repo.config
        self.as_of_year: int = int(cfg["as-of-year"])
        self.recent_max: int = int(cfg["age-thresholds"]["recent-max-age"])
        self.mid_max: int = int(cfg["age-thresholds"]["mid-max-age"])
        fm, _error = load_front_matter(page.front_matter)
        self.maturity: object = fm.get("maturity") if fm else None

    def add(self, code: str, line: int, message: str) -> None:
        self.findings.append(Finding(code, self.path, line, message))

    def run(self) -> None:
        for fence in colon_managed_fences(self.page):
            self.add("B06", fence.start + 1, "managed blocks must use backtick fences, not colon fences")
        for block in self.page.blocks:
            self.check_block(block)
        if self.entry.kind == "chapter":
            self.check_lesson_order()
            self.check_section_rules(("T02", "R03"))
        self.check_stub_thin()
        self.check_risk_titles()
        hb_badges.check_page(self)

    # -- blocks ---------------------------------------------------------------

    def check_block(self, block: Block) -> None:
        line = block.line
        class_kinds = block.class_kinds
        if len(class_kinds) != 1:
            self.add("B04", line, "the :class: option must carry exactly one of hb-lesson, hb-thin, hb-risk")
            return
        kind = next(iter(class_kinds))
        if block.field_line is None or block.parse_error:
            self.add("B01", line, f"field line does not parse: {block.parse_error or 'missing'}")
            return
        if not block.blank_after_field:
            self.add("B01", line, "a blank line must follow the field line")
        if block.kind != kind:
            self.add("B02", line, f"field line kind {block.kind!r} does not match the class-implied kind {kind!r}")
            return
        unknown = sorted(set(block.fields) - KEYS_BY_KIND[kind])
        if unknown:
            self.add("B02", line, f"unknown keys for {kind}: {', '.join(unknown)}")
        if block.directive != DIRECTIVE_BY_KIND[kind]:
            self.add("B03", line, f"{kind} blocks use {{{DIRECTIVE_BY_KIND[kind]}}}, found {{{block.directive}}}")
        names = [name for _i, name, _v in block.options]
        if names != ["class"]:
            self.add("B04", line, f"the only option must be :class: on the line after the opening; found {names}")
        self.check_placement(block, kind)
        match kind:
            case "lesson":
                self.check_lesson(block)
            case "thin":
                self.check_thin(block)
            case "risk":
                self.check_risk(block)

    def check_placement(self, block: Block, kind: BlockKind) -> None:
        page_kind, section = self.entry.kind, block.section
        match kind:
            case "lesson":
                scope = block.fields.get("scope")
                wanted = SEC_CASES if scope == "specific" else SEC_PRINCIPLES
                ok = page_kind == "chapter" and section == wanted
                where = f"a chapter's {wanted!r} section"
            case "thin":
                ok = (page_kind == "chapter" and section == SEC_THIN) or page_kind in ("page", "annex", "appendix")
                where = "a chapter's 'Thin content' section, or a page, annex or appendix"
            case "risk":
                ok = (page_kind == "chapter" and section == SEC_RISKS) or self.entry.id == "cross-cutting-risks"
                where = "a chapter's 'Risks' section or the cross-cutting-risks page"
        if not ok:
            self.add("B05", block.line, f"{kind} block (scope {block.fields.get('scope', '-')}) is only allowed in {where}; found in {page_kind} section {section!r}")

    def check_author_title(self, block: Block, code: str) -> None:
        if not 1 <= len(block.title) <= 80 or "`" in block.title:
            self.add(code, block.line, "the title must be 1 to 80 characters without backticks")

    def check_thin(self, block: Block) -> None:
        f, line = block.fields, block.line
        self.check_author_title(block, "B03")
        for key in ("kind", "needs", "who-might-know"):
            if key not in f:
                self.add("T01", line, f"thin block needs {key!r}")
        if "kind" in f and f["kind"] not in THIN_KINDS:
            self.add("T01", line, f"thin kind {f['kind']!r} is not one of {', '.join(sorted(THIN_KINDS))}")
        if "area" in f and f["area"] not in THIN_AREAS:
            self.add("T01", line, f"area {f['area']!r} is not an allowed thin area")
        if "issue" in f and not ISSUE_RE.match(f["issue"]):
            self.add("T01", line, f"issue {f['issue']!r} is not '#<n>' or a GitHub issue URL")
        if "since" in f and not _is_date(f["since"]):
            self.add("T01", line, f"since {f['since']!r} is not an ISO date")
        if f.get("kind") in THIN_KINDS:
            self.compare_classes(block, {"hb-thin", f"hb-thin-{f['kind']}"})

    def check_risk(self, block: Block) -> None:
        f, line = block.fields, block.line
        self.check_author_title(block, "B03")
        for key in ("likelihood", "impact", "mitigation"):
            if key not in f:
                self.add("R01", line, f"risk block needs {key!r}")
        for key in ("likelihood", "impact"):
            if key in f and f[key] not in LEVELS:
                self.add("R01", line, f"{key} {f[key]!r} is not low, medium or high")
        if "mitigation" in f and len(f["mitigation"]) > 300:
            self.add("R01", line, "mitigation is longer than 300 characters")
        if "playbook" in f:
            target = self.repo.entries_by_id.get(f["playbook"])
            if target is None or target.kind != "playbook":
                self.add("R02", line, f"playbook {f['playbook']!r} is not a chapter-list entry of kind playbook")
        if f.get("likelihood") in LEVELS and f.get("impact") in LEVELS:
            self.compare_classes(block, {"hb-risk", f"hb-likelihood-{f['likelihood']}", f"hb-impact-{f['impact']}"})

    def compare_classes(self, block: Block, expected: set[str]) -> None:
        if set(block.classes) != expected or len(block.classes) != len(set(block.classes)):
            self.add("B04", block.line, f"class tokens {sorted(block.classes)} do not equal the computed set {sorted(expected)}")

    # -- lessons --------------------------------------------------------------

    def check_lesson(self, block: Block) -> None:
        f, line = block.fields, block.line
        errors = self.lesson_field_errors(f)
        for code, message in errors:
            self.add(code, line, message)
        structural_ok = not any(code in ("L01", "L02") for code, _m in errors)
        self.lessons.append(Lesson(self.entry, self.path, block, f, structural_ok))
        if structural_ok:
            title = lesson_title(f, self.as_of_year, self.recent_max, self.mid_max)
            if block.title != title:
                self.add("L05", line, f"title {block.title!r} must equal the computed {title!r}")
            expected = lesson_classes(f, self.as_of_year, self.recent_max, self.mid_max)
            if set(block.classes) != expected or len(block.classes) != len(set(block.classes)):
                self.add("L05", line, f"class tokens {sorted(block.classes)} must equal the computed {sorted(expected)}")
        self.check_lesson_evidence(block, f, structural_ok)

    def lesson_field_errors(self, f: dict[str, str]) -> list[tuple[str, str]]:
        errors: list[tuple[str, str]] = []
        scope = f.get("scope")
        for key in ("scope", "source", "ledger", "confidence", "status"):
            if key not in f:
                errors.append(("L01", f"lesson needs {key!r}"))
        if scope not in ("general", "specific"):
            errors.append(("L01", f"scope {scope!r} is not general or specific"))
            return errors
        if scope == "specific":
            for key in ("year", "place", "org"):
                if key not in f:
                    errors.append(("L01", f"a specific lesson needs {key!r}"))
            for key in ("basis", "reason"):
                if key in f:
                    errors.append(("L01", f"{key!r} is forbidden on a specific lesson"))
        else:
            for key in ("year", "place", "org"):
                if key in f:
                    errors.append(("L01", f"{key!r} is forbidden on a general lesson"))
            if f.get("basis") not in ("independent-conferences", "structural"):
                errors.append(("L01", "a general lesson needs basis: independent-conferences or structural"))
            if f.get("basis") == "structural" and "reason" not in f:
                errors.append(("L01", "basis: structural needs a reason"))
            if f.get("basis") != "structural" and "reason" in f:
                errors.append(("L01", "reason is only allowed with basis: structural"))
            if len(f.get("reason", "")) > 200:
                errors.append(("L01", "reason is longer than 200 characters"))
        if "year" in f:
            if not f["year"].isdigit() or int(f["year"]) < 2000:
                errors.append(("L01", f"year {f['year']!r} is not an integer from 2000"))
            elif int(f["year"]) > self.as_of_year:
                errors.append(("L02", f"year {f['year']} is after as-of-year {self.as_of_year}"))
        if "place" in f and not 1 <= len(f["place"]) <= 40:
            errors.append(("L01", "place must be 1 to 40 characters"))
        if "org" in f and not 1 <= len(f["org"]) <= 60:
            errors.append(("L01", "org must be 1 to 60 characters"))
        errors.extend(self.id_list_errors(f, "source", "source-id-pattern"))
        errors.extend(self.id_list_errors(f, "ledger", "ledger-id-pattern"))
        if "conflicts-with" in f:
            errors.extend(self.id_list_errors(f, "conflicts-with", "ledger-id-pattern"))
        if "confidence" in f and f["confidence"] not in CONFIDENCE_ORDER:
            errors.append(("L01", f"confidence {f['confidence']!r} is not observed, reported or hearsay"))
        if "status" in f and f["status"] not in ("active", "contested", "superseded"):
            errors.append(("L01", f"status {f['status']!r} is not active, contested or superseded"))
        if "context" in f:
            for token in f["context"].split(";"):
                message = validate_context_token(token.strip(), allow_bare=False)
                if message:
                    errors.append(("L01", f"context: {message}"))
        errors.extend(self.status_link_errors(f))
        return errors

    def id_list_errors(self, f: dict[str, str], key: str, pattern_key: str) -> list[tuple[str, str]]:
        if key not in f:
            return []
        items = split_list(f[key])
        pattern = self.repo.pattern(pattern_key)
        bad = [item for item in items if not pattern.fullmatch(item)]
        errors = [("L01", f"{key} item {item!r} does not match {pattern.pattern}") for item in bad]
        if len(set(items)) != len(items):
            errors.append(("L01", f"{key} lists an ID twice"))
        return errors

    def status_link_errors(self, f: dict[str, str]) -> list[tuple[str, str]]:
        errors: list[tuple[str, str]] = []
        status = f.get("status")
        if status == "contested" and not ISSUE_RE.match(f.get("issue", "")):
            errors.append(("L07", "a contested lesson needs issue: '#<n>' or a GitHub issue URL"))
        if status != "contested" and "issue" in f:
            errors.append(("L07", "issue is only allowed on a contested lesson"))
        if status == "superseded" and not self.repo.pattern("ledger-id-pattern").fullmatch(f.get("by", "")):
            errors.append(("L07", "a superseded lesson needs by: <one ledger ID>"))
        if status != "superseded" and "by" in f:
            errors.append(("L07", "by is only allowed on a superseded lesson"))
        return errors

    def check_lesson_evidence(self, block: Block, f: dict[str, str], structural_ok: bool) -> None:
        line = block.line
        sources = [s for s in split_list(f.get("source", "")) if s]
        for source in sources:
            if source not in self.repo.manifest:
                self.add("L03", line, f"source {source} is not in the source manifest")
        rows: list[dict[str, Any]] = []
        for ledger_id in [i for i in split_list(f.get("ledger", "")) if i]:
            row = self.repo.ledger_rows.get(ledger_id)
            if row is None:
                self.add("L03", line, f"ledger ID {ledger_id} is not in the ledger")
                continue
            rows.append(row)
            placement, _error = parse_disposition(row.get("disposition"))
            if placement is None:
                self.add("L10", line, f"{ledger_id} is not placed (dropped rows are never cited by a lesson)")
            elif placement.page != self.entry.id or anchor_error(self.repo, placement.page, placement.slug, purpose="disposition"):
                self.add("L10", line, f"{ledger_id} is placed at {row.get('disposition')!r}, not at a valid section of {self.entry.id!r}")
        if not structural_ok or not rows or len(rows) != len([i for i in split_list(f.get("ledger", "")) if i]):
            return
        if f.get("scope") == "specific":
            self.check_specific_rows(line, f, rows)
        elif f.get("scope") == "general" and f.get("basis") == "independent-conferences":
            pairs = {(r.get("year"), r.get("place")) for r in rows}
            orgs = {str(r.get("org", "")).strip().casefold() for r in rows}
            if len(pairs) < 3 or len(orgs) < 2:
                self.add("L08", line, f"promotion needs 3 distinct (year, place) pairs and 2 organizing bodies; found {len(pairs)} and {len(orgs)}")

    def check_specific_rows(self, line: int, f: dict[str, str], rows: list[dict[str, Any]]) -> None:
        for row in rows:
            same = (str(row.get("year")), row.get("place"), row.get("org")) == (f.get("year"), f.get("place"), f.get("org"))
            if not same:
                self.add("L04", line, f"ledger row {row.get('ledger_id')} has a different year, place or org")
        union = {str(r.get("source_id")) for r in rows}
        if set(split_list(f.get("source", ""))) != union:
            self.add("L04", line, f"source must equal the cited rows' source IDs {sorted(union)}")
        weakest = max((str(r.get("confidence")) for r in rows), key=lambda c: CONFIDENCE_ORDER.get(c, 9))
        if f.get("confidence") != weakest:
            self.add("L04", line, f"confidence must equal the weakest row confidence {weakest!r}")

    def check_lesson_order(self) -> None:
        def first_ledger(lesson: Lesson) -> str:
            return lesson.ledger_ids[0] if lesson.ledger_ids else ""

        valid = [l for l in self.lessons if l.valid]
        cases = [l for l in valid if l.block.section == SEC_CASES and l.fields["scope"] == "specific"]
        principles = [l for l in valid if l.block.section == SEC_PRINCIPLES and l.fields["scope"] == "general"]
        case_keys = [(-int(l.fields["year"]), CONFIDENCE_ORDER[l.fields["confidence"]], first_ledger(l)) for l in cases]
        for (a, b), lesson in zip(zip(case_keys, case_keys[1:]), cases[1:]):
            if b < a:
                self.add("L06", lesson.block.line, "case notes must be ordered by year descending, then confidence, then first ledger ID")
        keys = [first_ledger(l) for l in principles]
        for (a, b), lesson in zip(zip(keys, keys[1:]), principles[1:]):
            if b < a:
                self.add("L06", lesson.block.line, "general lessons must be ordered by first ledger ID ascending")

    # -- sections -------------------------------------------------------------

    def check_section_rules(self, wanted: tuple[str, ...]) -> None:
        for code, heading, block_kind, prefix in (
            ("T02", SEC_THIN, "thin", NONE_KNOWN_PREFIX),
            ("R03", SEC_RISKS, "risk", NO_RISKS_PREFIX),
        ):
            if code not in wanted:
                continue
            section = next((s for s in self.page.sections() if s.heading.text == heading), None)
            if section is None:
                self.add(code, 1, f"section {heading!r} is missing")
                continue
            blocks = [b for b in self.page.blocks if section.start <= b.fence.start < section.end and block_kind in b.class_kinds]
            if blocks:
                continue
            lines = content_lines(self.page, section.start + 1, section.end)
            text = lines[0][1].strip() if len(lines) == 1 else ""
            ok = text.startswith(prefix) and _sentence_ok(code, text[len(prefix):])
            if not ok:
                expected = "a thin block or 'None known as of YYYY-MM-DD.'" if code == "T02" else "a risk block or 'No chapter-specific risks recorded. Rationale: <one sentence>.'"
                self.add(code, section.start + 1, f"section {heading!r} must hold {expected}")

    def check_stub_thin(self) -> None:
        if self.maturity != "stub" or self.entry.kind not in ("chapter", "page", "annex", "appendix"):
            return
        if not any("thin" in b.class_kinds for b in self.page.blocks):
            self.add("T02", 1, "a stub page must hold at least one thin block")

    def check_risk_titles(self) -> None:
        seen: set[str] = set()
        for block in self.page.blocks:
            if "risk" not in block.class_kinds:
                continue
            slug = slugify(block.title)
            if slug in seen:
                self.add("R04", block.line, f"risk title {block.title!r} is not unique on this page")
            seen.add(slug)


def _is_date(text: str) -> bool:
    if not ISO_DATE_RE.match(text):
        return False
    try:
        dt.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def _sentence_ok(code: str, rest: str) -> bool:
    if code == "T02":
        return rest.endswith(".") and _is_date(rest[:-1])
    return len(rest) > 1 and rest.endswith(".")


def check_pages(repo: Repo) -> tuple[list[Finding], list[Lesson], dict[str, Page]]:
    findings: list[Finding] = []
    lessons: list[Lesson] = []
    pages: dict[str, Page] = {}
    for entry in repo.written_entries():
        path = repo.path(entry.path)
        if not path.is_file():
            continue
        page = parse_page(path)
        pages[entry.id] = page
        checker = PageChecker(repo, entry, page)
        checker.run()
        findings.extend(checker.findings)
        lessons.extend(checker.lessons)
    return findings, lessons, pages


def check_cross_page(repo: Repo, lessons: list[Lesson], pages: dict[str, Page]) -> list[Finding]:
    """L09 (contradictions) and L10 (b) (every placed row appears in its section)."""
    findings: list[Finding] = []
    by_ledger: dict[str, list[Lesson]] = {}
    for lesson in lessons:
        for ledger_id in lesson.ledger_ids:
            by_ledger.setdefault(ledger_id, []).append(lesson)
    for lesson in lessons:
        if lesson.fields.get("status") != "active":
            continue
        for other_id in split_list(lesson.fields.get("conflicts-with", "")):
            for other in by_ledger.get(other_id, []):
                if other is lesson or other.fields.get("status") != "active":
                    continue
                if not contexts_distinguish(lesson.fields.get("context"), other.fields.get("context")):
                    findings.append(Finding("L09", lesson.path, lesson.block.line, f"conflicts with active lesson citing {other_id} ({other.path}:{other.block.line}) and no context distinguishes them"))
    findings.extend(placed_rows_present(repo, pages, "L10"))
    return findings


def placed_rows_present(repo: Repo, pages: dict[str, Page], code: str) -> list[Finding]:
    """Row to page: a row placed at a written page appears in the named section."""
    findings: list[Finding] = []
    for ledger_id, row in sorted(repo.ledger_rows.items()):
        placement, _error = parse_disposition(row.get("disposition"))
        if placement is None or placement.page not in pages:
            continue
        if anchor_error(repo, placement.page, placement.slug, purpose="disposition"):
            continue  # an invalid target is reported by LD09 and G9
        page = pages[placement.page]
        if placement.slug is None:
            start, end = page.body_start, len(page.lines)
        else:
            section = page.section_by_slug(placement.slug)
            if section is None:
                findings.append(Finding(code, rel(repo, page.path), 1, f"{ledger_id} is placed at #{placement.slug}, which is not a section of the page"))
                continue
            start, end = section.start, section.end
        token = repo.token_regex("ledger-id-pattern")
        found = any(m.group(0) == ledger_id for j in range(start, end) for m in token.finditer(page.lines[j]))
        if not found:
            findings.append(Finding(code, rel(repo, page.path), start + 1, f"{ledger_id} is placed here but does not appear in this section"))
    return findings


def check(repo: Repo) -> list[Finding]:
    findings, lessons, pages = check_pages(repo)
    return findings + check_cross_page(repo, lessons, pages)


def page_rule_findings(repo: Repo, entry: Entry, page: Page, wanted: tuple[str, ...]) -> list[Finding]:
    """The G4 hook: N01, R03 and T02 for one page."""
    checker = PageChecker(repo, entry, page)
    checker.check_section_rules(wanted)
    if "N01" in wanted:
        hb_badges.check_page(checker)
    if "T02" in wanted:
        checker.check_stub_thin()
    return [f for f in checker.findings if f.code in wanted]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    return report(check(Repo(args.root)), "G5 conventions")


if __name__ == "__main__":
    sys.exit(main())
