"""Gate G4: chapter contract (chapter-template.md, section 8; front-matter.md, section 4).

``check_entry`` validates one chapter-list entry; the pytest suite runs it for
every entry and marks ``status: planned`` entries ``xfail(strict=True)``.
The CLI checks written entries only.

Codes: CL01 chapter list schema; C00 file missing; C01 H1; C02 headings;
C03 "Applies when" tokens; C04 section rules (N01, R03, T02 are reported under
their own codes); C05 source IDs; C06 word budget; C07 maturity minimums;
C10 page headings; C11 playbook structure; C12 annex disclaimer;
C13 generated header; C14 templates referenced; F01-F09 front matter.

Usage: venv/bin/python scripts/lint/g4_contract.py [--root PATH] [--as-of YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import datetime as dt
import posixpath
import re
import sys
from pathlib import Path

import hb_frontmatter
from g5_conventions import page_rule_findings
from hb_common import (
    CHAPTER_HEADINGS,
    ENTRY_KEYS,
    ID_RE,
    KINDS,
    PARTS,
    PLAYBOOK_HEADINGS,
    REPO_ROOT,
    STATUSES,
    Entry,
    Finding,
    Repo,
    rel,
    report,
    validate_context_token,
)
from hb_markdown import ADMONITIONS, OPTION_RE, Page, content_lines, list_items, parse_page, prose_lines, strip_list_marker

ANNEX_DISCLAIMER = (
    "This annex is general information, not legal, tax or insurance advice. "
    "Check current rules with a qualified local adviser."
)
GENERATED_HEADER = "<!-- generated: do not edit; run the generator -->"
TOKEN_BULLET_RE = re.compile(r"^`([^`]+)`\s+\S")
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
DOC_ROLE_RE = re.compile(r"\{doc\}`(?:[^`<]*<)?([^`>]+)>?`")
MIN_SOURCES = {"stub": 0, "draft": 1, "reviewed": 2, "proven": 3}


def chapter_list_findings(repo: Repo) -> list[Finding]:
    """Schema of docs/spec/chapter-list.yml (chapter-template.md, section 1)."""
    path = repo.config["paths"]["chapter-list"]
    findings: list[Finding] = []
    seen: set[str] = set()
    raw = repo.raw_chapter_list
    if not raw:
        return [Finding("CL01", path, 1, "chapter list has no entries")]
    for number, item in enumerate(raw, start=1):
        where = f"entry {number}"
        if not isinstance(item, dict) or sorted(item) != sorted(ENTRY_KEYS):
            findings.append(Finding("CL01", path, 1, f"{where}: keys must be exactly {', '.join(ENTRY_KEYS)}"))
            continue
        if not all(isinstance(item[k], str) for k in ENTRY_KEYS):
            findings.append(Finding("CL01", path, 1, f"{where}: every value must be a string"))
            continue
        checks = (
            (ID_RE.match(item["id"]), f"id {item['id']!r} is not a lowercase slug"),
            (item["id"] not in seen, f"id {item['id']!r} is duplicated"),
            (item["part"] in PARTS, f"part {item['part']!r} is not allowed"),
            (item["kind"] in KINDS, f"kind {item['kind']!r} is not allowed"),
            (item["status"] in STATUSES, f"status {item['status']!r} is not allowed"),
            (item["path"].startswith("docs/") and item["path"].endswith(".md"), f"path {item['path']!r} must be docs/....md"),
            (item["title"].strip() == item["title"] and item["title"], "title must be non-empty"),
        )
        findings.extend(Finding("CL01", path, 1, f"{where}: {msg}") for ok, msg in checks if not ok)
        seen.add(item["id"])
    paths = [e.path for e in repo.entries]
    for dup in sorted({p for p in paths if paths.count(p) > 1}):
        findings.append(Finding("CL01", path, 1, f"path {dup!r} is listed twice"))
    return findings


class ContractChecker:
    def __init__(self, repo: Repo, entry: Entry, as_of: dt.date) -> None:
        self.repo: Repo = repo
        self.entry: Entry = entry
        self.as_of: dt.date = as_of
        self.path: str = entry.path
        self.findings: list[Finding] = []

    def add(self, code: str, line: int, message: str) -> None:
        self.findings.append(Finding(code, self.path, line, message))

    def run(self) -> list[Finding]:
        file = self.repo.path(self.entry.path)
        if not file.is_file():
            self.add("C00", 0, f"file for {self.entry.id!r} does not exist")
            return self.findings
        page = parse_page(file)
        fm = self.check_front_matter(page)
        self.check_h1(page)
        match self.entry.kind:
            case "chapter":
                self.check_chapter(page, fm)
            case "playbook":
                self.check_headings(page, PLAYBOOK_HEADINGS, "C11")
                self.check_playbook(page)
            case "annex":
                self.check_free_headings(page)
                self.check_annex(page)
            case "generated":
                self.check_free_headings(page)
            case _:
                self.check_free_headings(page)
        return self.findings

    def check_front_matter(self, page: Page) -> dict[str, object]:
        if page.front_matter_error:
            self.add("F01", 1, page.front_matter_error)
            return {}
        fm, error = hb_frontmatter.load(page.front_matter)
        if fm is None:
            self.add("F01", 1, error or "front matter missing")
            return {}
        for code, message in hb_frontmatter.check(self.repo, self.entry, fm, self.as_of):
            self.add(code, 1, message)
        return fm

    def check_h1(self, page: Page) -> None:
        h1s = [h for h in page.headings if h.level == 1]
        if len(h1s) != 1 or h1s[0].text != self.entry.title:
            self.add("C01", h1s[0].index + 1 if h1s else 1, f"exactly one H1 equal to {self.entry.title!r} is required (found {[h.text for h in h1s]})")
            return
        before = content_lines(page, page.body_start, h1s[0].index)
        allowed = [GENERATED_HEADER] if self.entry.kind == "generated" else []
        texts = [t.strip() for _i, t in before if not re.match(r"^\([^)]*\)=$", t.strip())]
        if texts != allowed:
            if self.entry.kind == "generated":
                self.add("C13", 1, f"the first line after the front matter must be {GENERATED_HEADER!r}, followed by the H1")
            else:
                self.add("C01", h1s[0].index + 1, "the H1 must be the first content after the front matter")
        if page.headings and page.headings[0].level != 1:
            self.add("C01", page.headings[0].index + 1, "the H1 must be the first heading")

    def check_headings(self, page: Page, wanted: tuple[str, ...], code: str) -> None:
        h2 = [h.text for h in page.headings if h.level == 2]
        if tuple(h2) != wanted:
            self.add(code, 1, f"H2 headings must be exactly {list(wanted)} in order; found {h2}")
        for heading in page.headings:
            if heading.level >= 4:
                self.add(code, heading.index + 1, f"H{heading.level} is not allowed (H3 is the deepest)")
        h1 = next((h for h in page.headings if h.level == 1), None)
        first_h2 = next((h for h in page.headings if h.level == 2), None)
        if h1 and first_h2 and self.entry.kind == "chapter":
            if content_lines(page, h1.index + 1, first_h2.index):
                self.add(code, h1.index + 2, "nothing may stand between the H1 and the first H2")

    def check_free_headings(self, page: Page) -> None:
        for heading in page.headings:
            if heading.level >= 4:
                self.add("C10", heading.index + 1, f"H{heading.level} is not allowed (H2 and H3 only)")

    # -- chapter ---------------------------------------------------------------

    def check_chapter(self, page: Page, fm: dict[str, object]) -> None:
        self.check_headings(page, CHAPTER_HEADINGS, "C02")
        self.check_applies_when(page, fm)
        self.findings.extend(page_rule_findings(self.repo, self.entry, page, ("N01", "R03", "T02")))
        cited = self.check_sources(page)
        self.check_word_budget(page)
        self.check_maturity(page, fm, cited)

    def check_applies_when(self, page: Page, fm: dict[str, object]) -> None:
        section = page.section_by_slug("applies-when")
        if section is None:
            return
        tokens: list[str] = []
        for start, _end, indent in list_items(page.lines, section.start + 1, section.end, page.in_fence):
            if indent:
                continue
            match = TOKEN_BULLET_RE.match(strip_list_marker(page.lines[start]))
            if not match:
                self.add("C03", start + 1, "each bullet starts with one context token in backticks, then a sentence")
                continue
            token = match.group(1)
            message = None if token == "all" else validate_context_token(token, allow_bare=True)
            if message:
                self.add("C03", start + 1, message)
            tokens.append(token)
        if not tokens:
            self.add("C03", section.start + 1, "'Applies when' needs at least one token bullet")
        applies = fm.get("applies-to")
        if isinstance(applies, list) and set(tokens) != set(map(str, applies)):
            self.add("F06", section.start + 1, f"'Applies when' tokens {sorted(tokens)} must equal applies-to {sorted(map(str, applies))}")

    def check_sources(self, page: Page) -> set[str]:
        token = self.repo.token_regex("source-id-pattern")
        section = page.section_by_slug("sources-and-further-reading")
        listed: set[str] = set()
        if section is not None:
            further = next((h.index for h in page.headings if h.level == 3 and section.start < h.index < section.end and h.text == "Further reading"), section.end)
            for start, _end, indent in list_items(page.lines, section.start + 1, further, page.in_fence):
                match = token.match(strip_list_marker(page.lines[start]))
                if indent == 0 and match:
                    listed.add(match.group(0))
        used = {m.group(0) for j in prose_lines(page) for m in token.finditer(page.lines[j])}
        for source in sorted(used - listed):
            self.add("C05", 1, f"{source} is used on the page but not listed in 'Sources and further reading'")
        for source in sorted(used):
            if source not in self.repo.manifest:
                self.add("C05", 1, f"{source} is not in the source manifest")
        return listed

    def check_word_budget(self, page: Page) -> None:
        """Counting rules of chapter-template.md, section 5."""
        sources = page.section_by_slug("sources-and-further-reading")
        stop = sources.start if sources else len(page.lines)
        skipped: set[int] = set()
        titles: dict[int, str] = {}
        for fence in page.fences:
            if fence.directive in ADMONITIONS:
                titles[fence.start] = fence.argument
                skipped.add(fence.end)
                skipped.update(j for j in range(fence.start + 1, fence.end) if OPTION_RE.match(page.lines[j]))
            else:
                skipped.update(range(fence.start, fence.end + 1))
        words = 0
        for j in range(page.body_start, stop):
            line = page.lines[j]
            if j in skipped or line.lstrip().startswith("%"):
                continue
            words += len(titles.get(j, line).split())
        budget = int(self.repo.config["word-budget"])
        if words > budget:
            self.add("C06", 1, f"{words} words exceed the word budget of {budget}; split the chapter")

    def check_maturity(self, page: Page, fm: dict[str, object], listed: set[str]) -> None:
        maturity = fm.get("maturity")
        if maturity not in MIN_SOURCES:
            return
        if maturity != "stub":
            for section in page.sections():
                if not content_lines(page, section.start + 1, section.end):
                    self.add("C07", section.start + 1, f"maturity {maturity} needs real content in {section.heading.text!r}")
        needed = MIN_SOURCES[str(maturity)]
        if len(listed) < needed:
            self.add("C07", 1, f"maturity {maturity} needs at least {needed} distinct source IDs; found {len(listed)}")

    # -- other kinds -----------------------------------------------------------

    def check_playbook(self, page: Page) -> None:
        if any("lesson" in b.class_kinds for b in page.blocks):
            self.add("C11", 1, "a playbook has no lesson blocks")
        sections = {s.slug: s for s in page.sections()}
        rules = (
            ("triggers", r"^[-*+] ", "a bullet list of triggers"),
            ("first-hour-actions", r"^[0-9]+[.)] ", "numbered first-hour steps"),
            ("owner-roles", r"^\|", "a table of roles and responsibilities"),
        )
        for slug, pattern, what in rules:
            section = sections.get(slug)
            if section and not any(re.match(pattern, t) for _j, t in content_lines(page, section.start + 1, section.end)):
                self.add("C11", section.start + 1, f"{section.heading.text!r} needs {what}")
        related = sections.get("related-chapters")
        if related is None:
            return
        targets = self.link_targets(page, related.start + 1, related.end)
        if not targets:
            self.add("C11", related.start + 1, "'Related chapters' needs links to chapter-list pages")
        for index, target in targets:
            if target not in self.repo.entries_by_path:
                self.add("C11", index + 1, f"link {target!r} does not resolve to a chapter-list page")

    def link_targets(self, page: Page, start: int, end: int) -> list[tuple[int, str]]:
        base = posixpath.dirname(self.entry.path)
        result: list[tuple[int, str]] = []
        for j in range(start, end):
            for match in MD_LINK_RE.finditer(page.lines[j]):
                href = match.group(1).split("#")[0]
                result.append((j, posixpath.normpath(posixpath.join(base, href)) if href else self.entry.path))
            for match in DOC_ROLE_RE.finditer(page.lines[j]):
                target = match.group(1)
                path = "docs" + target if target.startswith("/") else posixpath.join(base, target)
                result.append((j, posixpath.normpath(path) + ".md"))
        return result

    def check_annex(self, page: Page) -> None:
        h1 = next((h for h in page.headings if h.level == 1), None)
        if h1 is None:
            return
        after = content_lines(page, h1.index + 1, len(page.lines))
        first = " ".join(t.strip() for _j, t in after[:2])
        if not first.startswith(ANNEX_DISCLAIMER):
            self.add("C12", h1.index + 2, "the first lines after the H1 must be the annex disclaimer")


def check_entry(repo: Repo, entry: Entry, as_of: dt.date | None = None) -> list[Finding]:
    return ContractChecker(repo, entry, as_of or dt.date.today()).run()


def templates_referenced(repo: Repo) -> list[Finding]:
    """Every file under docs/_static/templates/ is referenced from a page (section 6.4)."""
    folder = repo.path("docs/_static/templates")
    if not folder.is_dir():
        return []
    text = "\n".join(p.read_text(encoding="utf-8") for p in repo.markdown_pages())
    return [
        Finding("C14", rel(repo, f), 0, "template is not referenced from any page")
        for f in sorted(folder.rglob("*"))
        if f.is_file() and f.name not in text
    ]


def check(repo: Repo, as_of: dt.date | None = None) -> list[Finding]:
    findings = chapter_list_findings(repo) + templates_referenced(repo)
    for entry in repo.written_entries():
        findings.extend(check_entry(repo, entry, as_of))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--as-of", type=dt.date.fromisoformat, default=None)
    args = parser.parse_args(argv)
    return report(check(Repo(args.root), args.as_of), "G4 chapter contract")


if __name__ == "__main__":
    sys.exit(main())
