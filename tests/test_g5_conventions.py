"""G5 convention validation: lesson, thin and risk blocks and level badges."""

from __future__ import annotations

import pytest

import g5_conventions
from conftest import MakeRepo, broken_cases, case_codes
from hb_common import Repo, codes


def test_fixed_tree_passes(make_repo: MakeRepo) -> None:
    assert g5_conventions.check(make_repo()) == []


@pytest.mark.parametrize("case", broken_cases("g5"))
def test_broken_case_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = g5_conventions.check(make_repo(f"g5/broken/{case}"))
    assert codes(findings) == case_codes(case), "\n".join(map(str, findings))


def test_lesson_title_matches_the_spec_examples() -> None:
    """conventions.md, section 3.3: the rendered title table with as-of-year 2026."""
    def title(**fields: str) -> str:
        return g5_conventions.lesson_title({"status": "active", **fields}, 2026, 3, 8)

    assert title(scope="general") == "[general]"
    assert title(scope="specific", year="2024", place="Utrecht") == "[specific \u00b7 2024 \u00b7 Utrecht \u00b7 2 y]"
    assert title(scope="specific", year="2018", place="Tokyo") == "[specific \u00b7 2018 \u00b7 Tokyo \u00b7 8 y]"
    assert title(scope="specific", year="2012", place="Arnhem", status="contested") == "[specific \u00b7 2012 \u00b7 Arnhem \u00b7 14 y] stale-prone contested"


def test_repository_conventions(real_repo: Repo) -> None:
    findings = g5_conventions.check(real_repo)
    assert findings == [], "\n".join(map(str, findings))
