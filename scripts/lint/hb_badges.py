"""Normative-level badge rules N01-N04 (conventions.md, section 1), part of gate G5."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from hb_common import MUST_STATUSES, Entry, Repo, slugify
from hb_ledger import parse_disposition
from hb_markdown import HEADING_RE, LIST_ITEM_RE, Page, list_items


class PageChecker(Protocol):
    """What the badge rules need from the G5 page checker."""

    @property
    def repo(self) -> Repo: ...
    @property
    def entry(self) -> Entry: ...
    @property
    def page(self) -> Page: ...
    def add(self, code: str, line: int, message: str) -> None: ...

ANY_BADGE_RE = re.compile(r"\{bdg(?:-[a-z-]+)?\}`(MUST|DEFAULT|OPTION)`")
GRAMMAR = {
    "MUST": re.compile(r"^\{bdg-danger\}`MUST` \(req: (?P<req>[^;)]+); as-of: (?P<asof>[0-9]{4}-[0-9]{2}-[0-9]{2})\)"),
    "DEFAULT": re.compile(r"^\{bdg-primary\}`DEFAULT` \(basis: (?P<basis>[^)]+)\)"),
    "OPTION": re.compile(r"^\{bdg-secondary\}`OPTION`(?! ?\()"),
}
GRAMMAR_CODE = {"MUST": "N02", "DEFAULT": "N03", "OPTION": "N01"}
BADGE_SECTIONS = ("decisions-you-must-make", "how-to", "principles-and-general-lessons")
DECIDE_BY_RE = re.compile(r"\(decide-by: T-[0-9]+[dwm]\)")
QUESTION_RE = re.compile(r"\*\*[^*]+\?\*\*")


@dataclass(frozen=True, slots=True)
class Badge:
    index: int
    column: int
    level: str
    positioned: bool  # first inline content of a list item or paragraph


def find_badges(checker: PageChecker) -> list[Badge]:
    page = checker.page
    managed = {j for b in page.blocks for j in range(b.fence.start, b.fence.end + 1)}
    badges: list[Badge] = []
    for index in range(page.body_start, len(page.lines)):
        line = page.lines[index]
        if page.in_fence[index] and index not in managed:
            continue
        for match in ANY_BADGE_RE.finditer(line):
            positioned = index not in managed and _first_content(page.lines, index, match.start(), page.body_start)
            badges.append(Badge(index, match.start(), match.group(1), positioned))
    return badges


def _first_content(lines: list[str], index: int, column: int, body_start: int) -> bool:
    line = lines[index]
    if HEADING_RE.match(line) or line.lstrip().startswith("|"):
        return False
    item = LIST_ITEM_RE.match(line)
    if item:
        return column == item.end()
    if column != len(line) - len(line.lstrip()):
        return False
    previous = lines[index - 1] if index > body_start else ""
    return not previous.strip() or bool(HEADING_RE.match(previous))


def check_page(checker: PageChecker) -> None:
    page, entry = checker.page, checker.entry
    badges = find_badges(checker)
    for badge in badges:
        line = badge.index + 1
        if not badge.positioned:
            checker.add("N04", line, "a badge must be the first inline content of a list item or paragraph, never in a heading, table, admonition title or block body")
            continue
        if entry.kind == "chapter":
            section = page.section_at(badge.index)
            slug = slugify(section.heading.text) if section else ""
            if slug not in BADGE_SECTIONS:
                checker.add("N04", line, f"badges are only allowed in sections 3 to 5; found in {slug or 'no section'!r}")
                continue
        text = page.lines[badge.index][badge.column :]
        match = GRAMMAR[badge.level].match(text)
        if match is None:
            checker.add(GRAMMAR_CODE[badge.level], line, f"{badge.level} badge does not follow the exact markup of conventions.md section 1.1")
            continue
        if badge.level == "MUST":
            _check_must(checker, line, match.group("req"), match.group("asof"))
        elif badge.level == "DEFAULT":
            _check_default(checker, line, match.group("basis"))
    if entry.kind == "chapter":
        _check_items(checker, badges)


def _check_must(checker: PageChecker, line: int, req: str, asof: str) -> None:
    repo = checker.repo
    if not repo.pattern("requirement-id-pattern").fullmatch(req):
        checker.add("N02", line, f"req {req!r} does not match the requirement ID pattern")
        return
    row = repo.register.get(req)
    if row is None:
        checker.add("N02", line, f"{req} is not a row in the requirements register")
        return
    if str(row.get("as-of")) != asof:
        checker.add("N02", line, f"as-of {asof} does not equal the register row's as-of {row.get('as-of')}")
    if row.get("status") not in MUST_STATUSES:
        checker.add("N02", line, f"{req} has status {row.get('status')!r}; a MUST needs verified-current or verified-changed")


def _check_default(checker: PageChecker, line: int, basis: str) -> None:
    repo = checker.repo
    ids = [item.strip() for item in basis.split(",")]
    pattern = repo.pattern("ledger-id-pattern")
    if len(ids) < 2 or any(not pattern.fullmatch(i) for i in ids) or ", ".join(ids) != basis:
        checker.add("N03", line, "basis must list at least two ledger IDs separated by ', '")
        return
    rows = []
    for ledger_id in ids:
        row = repo.ledger_rows.get(ledger_id)
        if row is None:
            checker.add("N03", line, f"basis {ledger_id} is not in the ledger")
            continue
        if row.get("confidence") == "hearsay":
            checker.add("N03", line, f"basis {ledger_id} is hearsay, which never supports a DEFAULT")
        if parse_disposition(row.get("disposition"))[0] is None:
            checker.add("N03", line, f"basis {ledger_id} is a dropped row")
        rows.append(row)
    conferences = {(r.get("year"), r.get("place")) for r in rows}
    if len(rows) == len(ids) and len(conferences) < 2:
        checker.add("N03", line, "basis rows must come from at least two distinct conferences (year and place)")


def _check_items(checker: PageChecker, badges: list[Badge]) -> None:
    page = checker.page
    positions = {b.index: b for b in badges}
    for section in page.sections():
        slug = section.slug
        if slug not in BADGE_SECTIONS:
            continue
        items = list_items(page.lines, section.start + 1, section.end, page.in_fence)
        if slug == "decisions-you-must-make":
            top = [item for item in items if item[2] == 0]
            if not top:
                checker.add("N01", section.start + 1, "section 3 needs a top-level bullet list of decisions")
            for start, end, _indent in top:
                _check_decision(checker, badges, start, end, positions.get(start))
            continue
        for pos, (start, end, indent) in enumerate(items):
            child = next((s for s, _e, i in items[pos + 1 :] if s < end and i > indent), end)
            count = sum(1 for b in badges if start <= b.index < child)
            if count > 1:
                checker.add("N04", start + 1, "a list item carries at most one badge")


def _check_decision(checker: PageChecker, badges: list[Badge], start: int, end: int, first: Badge | None) -> None:
    count = sum(1 for b in badges if start <= b.index < end)
    line = start + 1
    if count != 1 or first is None or not first.positioned:
        checker.add("N01", line, f"every decision carries exactly one level badge as its first content (found {count})")
    text = " ".join(checker.page.lines[start:end])
    if not QUESTION_RE.search(text):
        checker.add("N01", line, "a decision needs a bold question (**...?**)")
    if "(decide-by:" in text and not DECIDE_BY_RE.search(text):
        checker.add("N01", line, "decide-by must read '(decide-by: T-<n><d|w|m>)'")
