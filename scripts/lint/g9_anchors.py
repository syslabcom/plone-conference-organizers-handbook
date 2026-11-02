"""Gate G9: anchor check (chapter-template.md, section 2, "Anchors").

Resolves every cited anchor against chapter-list.yml and the fixed slug sets:
- ledger dispositions ``placed: <id>[#<slug>]``,
- reader scenario targets in tests/scenarios.yml,
- ``<id>#<slug>`` tokens in inline code on the T-minus checklist page.

Codes: A01 unknown id; A02 slug not valid for the page kind; A03 anchor
required or forbidden for the page kind; A04 generated page as a target.

Usage: venv/bin/python scripts/lint/g9_anchors.py [--root PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from hb_common import REPO_ROOT, Finding, Repo, rel, report
from hb_ledger import PLACED_RE, anchor_error, split_target

CHECKLIST_ID = "t-minus-checklist"
INLINE_ANCHOR_RE = re.compile(r"`([a-z][a-z0-9-]*)#([a-z][a-z0-9-]*)`")


def load_scenarios(repo: Repo) -> list[Any]:
    path = repo.config_path("scenarios")
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios") if isinstance(data, dict) else None
    return scenarios if isinstance(scenarios, list) else []


def check(repo: Repo) -> list[Finding]:
    findings: list[Finding] = []
    for path, data, _error in repo.ledger_docs:
        rows = data.get("rows") if isinstance(data, dict) else None
        for row in rows if isinstance(rows, list) else []:
            disposition = row.get("disposition") if isinstance(row, dict) else None
            match = PLACED_RE.match(disposition) if isinstance(disposition, str) else None
            if match:
                problem = anchor_error(repo, match.group(1), match.group(2), purpose="disposition")
                if problem:
                    findings.append(Finding(problem[0], rel(repo, path), 0, f"{row.get('ledger_id')}: {problem[1]}"))
    scenarios_path = repo.config["paths"]["scenarios"]
    for scenario in load_scenarios(repo):
        target = scenario.get("target") if isinstance(scenario, dict) else None
        if not isinstance(target, str):
            continue
        page, slug = split_target(target)
        problem = anchor_error(repo, page, slug, purpose="scenario")
        if problem:
            findings.append(Finding(problem[0], scenarios_path, 0, f"{scenario.get('id')}: {problem[1]}"))
    checklist = repo.entries_by_id.get(CHECKLIST_ID)
    if checklist is not None and repo.path(checklist.path).is_file():
        for number, line in enumerate(repo.path(checklist.path).read_text(encoding="utf-8").splitlines(), start=1):
            for match in INLINE_ANCHOR_RE.finditer(line):
                problem = anchor_error(repo, match.group(1), match.group(2), purpose="disposition")
                if problem:
                    findings.append(Finding(problem[0], checklist.path, number, problem[1]))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    return report(check(Repo(args.root)), "G9 anchors")


if __name__ == "__main__":
    sys.exit(main())
