"""Gate G3: temporal-word lint (chapter-template.md, section 7, rule 4).

Flags "currently", "recently", "this year", "last year", "now", "soon" and
"new" when the same source line carries no dated anchor (``YYYY-MM`` or
``YYYY-MM-DD``). One sentence per line is the house rule, so the line is the
sentence. Code fences, inline code, URLs, link targets and comments are not prose.

Usage: venv/bin/python scripts/lint/g3_temporal.py [--root PATH] [FILE ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from hb_common import REPO_ROOT, Finding, Repo, rel, report
from hb_markdown import parse_page, prose_lines

TEMPORAL_RE = re.compile(r"\b(currently|recently|this year|last year|now|soon|new)\b", re.IGNORECASE)
DATED_RE = re.compile(r"\b[0-9]{4}-[0-9]{2}(?:-[0-9]{2})?\b")
_NOISE = (
    re.compile(r"`[^`]*`"),  # inline code and role targets
    re.compile(r"\]\([^)]*\)"),  # Markdown link targets
    re.compile(r"<!--.*?-->"),  # HTML comments
    re.compile(r"<[^>]+>"),  # HTML tags and autolinks
    re.compile(r"https?://\S+"),  # bare URLs
)


def undated_temporal_words(text: str) -> list[str]:
    """The temporal words in one line of prose that lack a dated anchor on that line."""
    cleaned = text
    for pattern in _NOISE:
        cleaned = pattern.sub(" ", cleaned)
    if DATED_RE.search(cleaned):
        return []
    return [m.group(1) for m in TEMPORAL_RE.finditer(cleaned)]


def check_file(repo: Repo, path: Path) -> list[Finding]:
    page = parse_page(path)
    findings: list[Finding] = []
    for index in prose_lines(page):
        line = page.lines[index]
        stripped = line.strip()
        if stripped.startswith("%") or re.match(r"^:[A-Za-z0-9_-]+:", stripped):
            continue
        if page.in_fence[index] and re.match(r"^ {0,3}(`{3,}|:{3,})", line):
            stripped = re.sub(r"^ {0,3}(`{3,}|:{3,})\{[^}]*\}", "", line)
        for word in undated_temporal_words(stripped):
            findings.append(
                Finding("W01", rel(repo, path), index + 1, f"temporal word {word!r} without a dated anchor (write 'as of YYYY-MM')")
            )
    return findings


# Pages excluded from the repository-wide scan, with the reason each is exempt.
# docs/evidence/lessons-ledger.md is rendered by scripts/evidence/build_evidence.py
# verbatim from ledger row text: historical rows quote their sources, and ledger
# text is evidence that must not be reworded to satisfy a prose lint.
EXCLUDED_PAGES = ("docs/evidence/lessons-ledger.md",)


def check(repo: Repo, files: list[Path] | None = None) -> list[Finding]:
    """Scan every published Markdown page (docs/ except docs/spec/ and EXCLUDED_PAGES)."""
    targets = files if files is not None else repo.markdown_pages()
    return [f for path in targets if rel(repo, path) not in EXCLUDED_PAGES for f in check_file(repo, path)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    repo = Repo(args.root)
    return report(check(repo, [p.resolve() for p in args.files] or None), "G3 temporal words")


if __name__ == "__main__":
    sys.exit(main())
