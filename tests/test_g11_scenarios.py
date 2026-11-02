"""G11 reader-scenario reachability over the built HTML."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

import g11_scenarios
from conftest import REPO_ROOT, MakeRepo, broken_cases, case_codes
from g9_anchors import load_scenarios
from hb_common import Repo, codes


def test_fixed_site_reaches_every_scenario(make_repo: MakeRepo) -> None:
    assert g11_scenarios.check(make_repo("g11/fixed")) == []


@pytest.mark.parametrize("case", broken_cases("g11"))
def test_broken_site_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = g11_scenarios.check(make_repo(f"g11/broken/{case}"))
    assert codes(findings) == case_codes(case), "\n".join(map(str, findings))


def test_missing_build_is_reported(make_repo: MakeRepo) -> None:
    assert codes(g11_scenarios.check(make_repo())) == {"S04"}


def test_repository_scenario_schema(real_repo: Repo) -> None:
    assert g11_scenarios.schema_findings(real_repo) == []


def _scenario_params() -> list[Any]:
    repo = Repo(Path(os.environ.get("HANDBOOK_ROOT", REPO_ROOT)))
    params = []
    for scenario in load_scenarios(repo):
        entry = repo.entries_by_id.get(str(scenario.get("target", "")).split("#")[0])
        planned = entry is None or entry.status == "planned"
        marks = [pytest.mark.xfail(strict=True, reason="target page is planned")] if planned else []
        params.append(pytest.param(scenario, id=str(scenario.get("id")), marks=marks))
    return params


@pytest.mark.parametrize("scenario", _scenario_params())
def test_scenario_reachable(real_repo: Repo, scenario: dict[str, Any]) -> None:
    site = g11_scenarios.Site(real_repo.path("_build/html"))
    assert (site.root / "index.html").is_file(), "run make html before the test suite"
    findings = g11_scenarios.check_scenario(real_repo, site, scenario)
    assert findings == [], "\n".join(map(str, findings))
