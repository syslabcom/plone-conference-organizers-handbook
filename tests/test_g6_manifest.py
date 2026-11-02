"""G6 source manifest integrity."""

from __future__ import annotations

import pytest

import g6_manifest
from conftest import MakeRepo, broken_cases, case_codes
from hb_common import Repo, codes


def test_fixed_tree_passes(make_repo: MakeRepo) -> None:
    assert g6_manifest.check(make_repo()) == []


@pytest.mark.parametrize("case", broken_cases("g6"))
def test_broken_case_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = g6_manifest.check(make_repo(f"g6/broken/{case}"))
    assert codes(findings) == case_codes(case), "\n".join(map(str, findings))


def test_repository_manifest(real_repo: Repo) -> None:
    findings = g6_manifest.check(real_repo)
    assert findings == [], "\n".join(map(str, findings))
