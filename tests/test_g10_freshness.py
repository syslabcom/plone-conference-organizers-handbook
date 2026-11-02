"""G10 freshness report (report-only in pull-request CI)."""

from __future__ import annotations

import json
import subprocess
import sys

import g10_freshness
from conftest import AS_OF, REPO_ROOT, MakeRepo
from hb_common import Repo

SCRIPT = str(REPO_ROOT / "scripts/lint/g10_freshness.py")


def run(repo: Repo, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, SCRIPT, "--root", str(repo.root), "--as-of", AS_OF.isoformat(), *args],
        capture_output=True, text=True, check=False,
    )


def test_fixed_tree_has_no_overdue_page(make_repo: MakeRepo) -> None:
    repo = make_repo()
    assert g10_freshness.overdue_pages(repo, AS_OF) == []
    assert run(repo, "--fail-on-overdue").returncode == 0


def test_overdue_page_is_listed_and_fails_in_strict_mode(make_repo: MakeRepo) -> None:
    repo = make_repo("g10/broken/overdue-page")
    result = run(repo, "--format", "json", "--fail-on-overdue")
    assert result.returncode == 1
    assert json.loads(result.stdout) == [
        {"id": "finance", "title": "Finance", "path": "docs/workstreams/finance.md",
         "review_by": "2026-01-15", "steward": "unassigned", "deputy": "unassigned"}
    ]


def test_overdue_page_does_not_fail_report_mode(make_repo: MakeRepo) -> None:
    assert run(make_repo("g10/broken/overdue-page")).returncode == 0


def test_repository_freshness_report_runs(real_repo: Repo) -> None:
    result = run(real_repo, "--format", "json")
    assert result.returncode == 0, result.stderr
    assert isinstance(json.loads(result.stdout), list)
