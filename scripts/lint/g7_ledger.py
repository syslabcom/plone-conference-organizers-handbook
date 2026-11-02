"""Gate G7: ledger coverage and row validation (ledger-schema.md, LD01-LD11).

Every row of every ``data/ledger/*.yml`` file is validated, and every row must
carry a ``placed`` or ``dropped`` disposition. An empty or missing ledger
directory passes: the ledger grows while tasks T7a to T7f run.

Usage: venv/bin/python scripts/lint/g7_ledger.py [--root PATH]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import g8_privacy
from g5_conventions import check_pages, placed_rows_present
from hb_common import CONFIDENCE_ORDER, ISSUE_RE, REPO_ROOT, Finding, Repo, rel, report
from hb_ledger import anchor_error, parse_disposition
from hb_markdown import split_list

GROUP_RANGES = {"7a": (1000, 1999), "7b": (2000, 2999), "7c": (3000, 3999), "7d": (4000, 4999), "7e": (5000, 5999),
                "7f": (6000, 6999)}
REQUIRED = ("ledger_id", "topic", "scope", "year", "place", "org", "source_id", "text_kind",
            "quote_or_paraphrase", "confidence", "status", "disposition")
OPTIONAL = ("locator", "issue", "by")
ENUMS = {
    "scope": ("general", "specific"),
    "text_kind": ("quote", "paraphrase"),
    "confidence": tuple(CONFIDENCE_ORDER),
    "status": ("active", "contested", "superseded"),
}


class LedgerChecker:
    def __init__(self, repo: Repo) -> None:
        self.repo: Repo = repo
        self.findings: list[Finding] = []
        self.ids: dict[str, str] = {}
        self.as_of_year: int = int(repo.config["as-of-year"])

    def add(self, code: str, path: str, line: int, message: str) -> None:
        self.findings.append(Finding(code, path, line, message))

    def run(self) -> list[Finding]:
        for path, data, error in self.repo.ledger_docs:
            where = rel(self.repo, path)
            if error is not None:
                self.add("LD01", where, 0, f"not valid YAML: {error}")
                continue
            if not isinstance(data, dict) or set(data) != {"group", "rows"}:
                self.add("LD01", where, 0, "a ledger file has exactly the top-level keys 'group' and 'rows'")
                continue
            group = data["group"]
            if group not in GROUP_RANGES:
                self.add("LD01", where, 0, f"group {group!r} is not one of {', '.join(GROUP_RANGES)}")
                group = None
            if not isinstance(data["rows"], list):
                self.add("LD01", where, 0, "rows must be a list")
                continue
            for number, row in enumerate(data["rows"], start=1):
                self.check_row(where, number, group, row)
        for hit in g8_privacy.check_paths(self.repo, self.repo.ledger_files):
            self.add("LD11", hit.path, hit.line, f"{hit.code} {hit.message}")
        self.check_consistency()
        return self.findings

    def check_row(self, where: str, number: int, group: str | None, row: Any) -> None:
        label = f"row {number}"
        if not isinstance(row, dict):
            self.add("LD02", where, 0, f"{label} is not a mapping")
            return
        ledger_id = row.get("ledger_id")
        if isinstance(ledger_id, str):
            label = f"{label} ({ledger_id})"
        missing = [k for k in REQUIRED if k not in row]
        unknown = sorted(set(row) - set(REQUIRED) - set(OPTIONAL))
        if missing or unknown:
            self.add("LD02", where, 0, f"{label}: missing {missing or '-'}; unknown {unknown or '-'}")
        self.check_identity(where, label, group, row)
        self.check_values(where, label, row)
        self.check_disposition(where, label, row)

    def check_identity(self, where: str, label: str, group: str | None, row: dict[str, Any]) -> None:
        ledger_id = row.get("ledger_id")
        if not isinstance(ledger_id, str) or not self.repo.pattern("ledger-id-pattern").fullmatch(ledger_id):
            self.add("LD03", where, 0, f"{label}: ledger_id {ledger_id!r} does not match the pattern")
        else:
            if ledger_id in self.ids:
                self.add("LD03", where, 0, f"{label}: ledger_id also used in {self.ids[ledger_id]}")
            self.ids.setdefault(ledger_id, where)
            if group is not None:
                low, high = GROUP_RANGES[group]
                if not low <= int(ledger_id[2:]) <= high:
                    self.add("LD03", where, 0, f"{label}: {ledger_id} is outside the range L-{low}..L-{high} of group {group}")
        topic = self.repo.entries_by_id.get(str(row.get("topic")))
        if "topic" in row and (topic is None or topic.kind == "generated"):
            self.add("LD04", where, 0, f"{label}: topic {row.get('topic')!r} is not a non-generated chapter-list id")

    def check_values(self, where: str, label: str, row: dict[str, Any]) -> None:
        for key, allowed in ENUMS.items():
            if key in row and row[key] not in allowed:
                self.add("LD05", where, 0, f"{label}: {key} {row[key]!r} is not one of {', '.join(allowed)}")
        year = row.get("year")
        if "year" in row and (not isinstance(year, int) or isinstance(year, bool) or not 2000 <= year <= self.as_of_year):
            self.add("LD05", where, 0, f"{label}: year {year!r} is not an integer from 2000 to {self.as_of_year}")
        for key, limit in (("place", 40), ("org", 60)):
            if key in row and not (isinstance(row[key], str) and 1 <= len(row[key]) <= limit):
                self.add("LD05", where, 0, f"{label}: {key} must be a string of 1 to {limit} characters")
        source = row.get("source_id")
        if "source_id" in row:
            if not isinstance(source, str) or not self.repo.pattern("source-id-pattern").fullmatch(source):
                self.add("LD06", where, 0, f"{label}: source_id {source!r} does not match the pattern")
            elif source not in self.repo.manifest:
                self.add("LD06", where, 0, f"{label}: source_id {source} is not in the source manifest")
        text = row.get("quote_or_paraphrase")
        if "quote_or_paraphrase" in row:
            words = len(text.split()) if isinstance(text, str) else 0
            limit = int(self.repo.config["max-quote-words"]) if row.get("text_kind") == "quote" else 120
            if words == 0 or words > limit:
                self.add("LD07", where, 0, f"{label}: the text has {words} words; allowed 1 to {limit}")
        status = row.get("status")
        if (status == "contested") != ("issue" in row) or ("issue" in row and not ISSUE_RE.match(str(row["issue"]))):
            self.add("LD08", where, 0, f"{label}: issue is required exactly when status is contested, as '#<n>' or an issue URL")
        if (status == "superseded") != ("by" in row):
            self.add("LD08", where, 0, f"{label}: by is required exactly when status is superseded")

    def check_disposition(self, where: str, label: str, row: dict[str, Any]) -> None:
        placement, error = parse_disposition(row.get("disposition"))
        if error is not None:
            self.add("LD09", where, 0, f"{label}: {error}")
            return
        if placement is not None:
            problem = anchor_error(self.repo, placement.page, placement.slug, purpose="disposition")
            if problem is not None:
                self.add("LD09", where, 0, f"{label}: {problem[1]}")

    def check_consistency(self) -> None:
        rows = self.repo.ledger_rows
        for ledger_id, row in rows.items():
            if row.get("status") == "superseded" and str(row.get("by")) not in rows:
                self.add("LD08", "ledger", 0, f"{ledger_id}: by {row.get('by')!r} is not an existing row")
        _findings, lessons, pages = check_pages(self.repo)
        for finding in placed_rows_present(self.repo, pages, "LD10"):
            self.findings.append(finding)
        for lesson in lessons:
            for ledger_id in split_list(lesson.fields.get("ledger", "")):
                row = rows.get(ledger_id)
                placement = parse_disposition(row.get("disposition"))[0] if row else None
                if row is None or placement is None or placement.page != lesson.entry.id:
                    self.add("LD10", lesson.path, lesson.block.line, f"lesson cites {ledger_id}, which is missing, dropped or placed elsewhere")


def check(repo: Repo) -> list[Finding]:
    return LedgerChecker(repo).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    return report(check(Repo(args.root)), "G7 ledger coverage")


if __name__ == "__main__":
    sys.exit(main())
