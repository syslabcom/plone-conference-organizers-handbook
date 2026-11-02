"""G7 ledger coverage and row validation (LD01-LD11)."""

from __future__ import annotations

import shutil

import pytest

import g7_ledger
from conftest import MakeRepo, broken_cases, case_codes
from hb_common import Repo, codes


def test_fixed_tree_passes(make_repo: MakeRepo) -> None:
    assert g7_ledger.check(make_repo()) == []


def test_missing_ledger_directory_passes(make_repo: MakeRepo) -> None:
    """The ledger grows during T7a-T7e; no ledger files is not an error."""
    repo = make_repo()
    shutil.rmtree(repo.path("data/ledger"))
    repo.path("docs/workstreams/finance.md").unlink()  # its lessons cite ledger rows
    assert g7_ledger.check(repo) == []


@pytest.mark.parametrize("case", broken_cases("g7"))
def test_broken_case_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = g7_ledger.check(make_repo(f"g7/broken/{case}"))
    assert codes(findings) == case_codes(case), "\n".join(map(str, findings))


def test_repository_ledger(real_repo: Repo) -> None:
    findings = g7_ledger.check(real_repo)
    assert findings == [], "\n".join(map(str, findings))
