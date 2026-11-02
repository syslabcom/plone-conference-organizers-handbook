"""Gate G10: freshness report (front-matter.md, sections 2.3 and 5).

Lists every written, non-generated page whose ``review-by`` is before the
as-of date (default: today), with its steward and deputy.

This is the documented interface for the scheduled workflow of task T8:

    venv/bin/python scripts/lint/g10_freshness.py --format json

prints a JSON list of objects with the keys ``id``, ``title``, ``path``,
``review_by``, ``steward`` and ``deputy``; the workflow opens one issue per
object unless an open freshness issue for that ``id`` exists.

Exit codes: 0 by default (report-only, as in pull-request CI);
1 with ``--fail-on-overdue`` when at least one page is overdue.
A past review-by never fails the pull-request lint (front-matter.md 2.3).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from hb_common import REPO_ROOT, Repo
from hb_frontmatter import as_date, load
from hb_markdown import parse_page


@dataclass(frozen=True, slots=True)
class Overdue:
    id: str
    title: str
    path: str
    review_by: str
    steward: str
    deputy: str


def overdue_pages(repo: Repo, as_of: dt.date) -> list[Overdue]:
    result: list[Overdue] = []
    for entry in repo.written_entries():
        path = repo.path(entry.path)
        if entry.kind == "generated" or not path.is_file():
            continue
        fm, _error = load(parse_page(path).front_matter)
        if fm is None:
            continue
        review_by = as_date(fm.get("review-by"))
        if review_by is not None and review_by < as_of:
            result.append(
                Overdue(entry.id, entry.title, entry.path, review_by.isoformat(), str(fm.get("steward", "")), str(fm.get("deputy", "")))
            )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List written pages past their review-by date.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on-overdue", action="store_true")
    args = parser.parse_args(argv)
    pages = overdue_pages(Repo(args.root), args.as_of)
    if args.format == "json":
        print(json.dumps([asdict(p) for p in pages], indent=2))
    else:
        for page in pages:
            print(f"{page.path}: review-by {page.review_by} is past {args.as_of} (steward {page.steward}, deputy {page.deputy})")
        print(f"G10 freshness: {len(pages)} overdue page(s) as of {args.as_of}", file=sys.stderr)
    return 1 if pages and args.fail_on_overdue else 0


if __name__ == "__main__":
    sys.exit(main())
