"""G4 chapter contract: fixture proof, then one contract test per chapter-list entry."""

from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import g4_contract
from conftest import AS_OF, REPO_ROOT, MakeRepo, broken_cases, case_codes
from hb_common import Entry, Finding, Repo, codes

BROKEN = [c for c in broken_cases("g4") if not c.startswith("xpass")]


def contract_findings(repo: Repo) -> list[Finding]:
    return g4_contract.check(repo, AS_OF)


def test_fixed_tree_passes_the_contract(make_repo: MakeRepo) -> None:
    assert contract_findings(make_repo()) == []


@pytest.mark.parametrize("case", BROKEN)
def test_broken_case_fails_for_its_rule(make_repo: MakeRepo, case: str) -> None:
    findings = contract_findings(make_repo(f"g4/broken/{case}"))
    assert codes(findings) == case_codes(case), "\n".join(map(str, findings))


def test_xfail_strict_turns_an_unexpected_pass_into_a_failure(make_repo: MakeRepo) -> None:
    """A planned entry whose page already passes must fail the suite (chapter-template.md 1, rule 2)."""
    repo = make_repo("g4/broken/xpass-planned-entry")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(Path(__file__)), "-k", "test_chapter_contract and finance"],
        cwd=REPO_ROOT,
        env={**os.environ, "HANDBOOK_ROOT": str(repo.root), "HANDBOOK_AS_OF": AS_OF.isoformat()},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stdout
    assert "XPASS(strict)" in result.stdout


def _entries_for_parametrize() -> list[Any]:
    root = Path(os.environ.get("HANDBOOK_ROOT", REPO_ROOT))
    repo = Repo(root)
    params = []
    for entry in repo.entries:
        marks = [pytest.mark.xfail(strict=True, reason="status: planned")] if entry.status == "planned" else []
        params.append(pytest.param(entry, id=entry.id, marks=marks))
    return params


@pytest.mark.parametrize("entry", _entries_for_parametrize())
def test_chapter_contract(real_repo: Repo, entry: Entry) -> None:
    as_of = os.environ.get("HANDBOOK_AS_OF")
    findings = g4_contract.check_entry(real_repo, entry, dt.date.fromisoformat(as_of) if as_of else None)
    assert findings == [], "\n".join(map(str, findings))


def test_chapter_list_schema(real_repo: Repo) -> None:
    assert g4_contract.chapter_list_findings(real_repo) == []


def test_templates_are_referenced(real_repo: Repo) -> None:
    assert g4_contract.templates_referenced(real_repo) == []
