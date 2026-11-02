"""G8 privacy lint."""

from __future__ import annotations

import pytest

import g8_privacy
from conftest import MakeRepo, broken_cases, case_codes
from hb_common import Repo, codes


def test_fixed_tree_passes_with_allowlist_and_archive_exclusion(make_repo: MakeRepo) -> None:
    repo = make_repo("g8/fixed")
    assert repo.path("data/sources/files/raw-archive.html").is_file()
    assert g8_privacy.check(repo) == []


@pytest.mark.parametrize("case", broken_cases("g8"))
def test_broken_case_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = g8_privacy.check(make_repo(f"g8/broken/{case}"))
    assert codes(findings) == case_codes(case), "\n".join(map(str, findings))


def test_archive_and_fixtures_are_excluded_explicitly() -> None:
    assert "data/sources" in g8_privacy.EXCLUDED_DIRS
    assert "tests/fixtures" in g8_privacy.EXCLUDED_DIRS


def test_repository_privacy(real_repo: Repo) -> None:
    findings = g8_privacy.check(real_repo)
    assert findings == [], "\n".join(map(str, findings))
