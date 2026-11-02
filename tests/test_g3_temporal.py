"""G3 temporal-word lint."""

from __future__ import annotations

import pytest

import g3_temporal
from conftest import MakeRepo, broken_cases, case_codes
from hb_common import Repo, codes


def test_fixed_tree_passes(make_repo: MakeRepo) -> None:
    assert g3_temporal.check(make_repo("g3/fixed")) == []


@pytest.mark.parametrize("case", broken_cases("g3"))
def test_broken_case_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = g3_temporal.check(make_repo(f"g3/broken/{case}"))
    assert codes(findings) == case_codes(case)
    assert {f.message.split("'")[1] for f in findings} == {"currently", "soon"}


def test_repository_has_no_undated_temporal_words(real_repo: Repo) -> None:
    findings = g3_temporal.check(real_repo)
    assert findings == [], "\n".join(map(str, findings))
