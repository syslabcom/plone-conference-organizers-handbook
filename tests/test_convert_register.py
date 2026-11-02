"""The requirements register converter (Markdown to data/requirements-register.yml)."""

from __future__ import annotations

import datetime as dt
from typing import Any

import pytest
import yaml

import convert_register
from conftest import FIXTURES, MakeRepo
from hb_common import Repo


def convert(repo: Repo, case: str) -> dict[str, Any]:
    return convert_register.convert((FIXTURES / "register" / case / "register.md").read_text(encoding="utf-8"), repo, "fixture")


def test_fixed_register_converts_every_column(make_repo: MakeRepo) -> None:
    data = convert(make_repo(), "fixed")
    first, second = data["rows"]
    assert (first["id"], second["id"]) == ("R-001", "R-002")
    assert first["as-of"] == dt.date(2026, 11, 2)
    assert first["source-ids"] == ["S001", "S002"]
    assert first["target-chapter-ids"] == ["finance"]
    assert second["source-force"] is None
    assert second["unresolved-sources"] == ["BIB/files/missing.txt"]
    assert second["target-chapter-ids"] == ["venue-loss"]
    assert second["unresolved-target-chapters"] == ["Nowhere"]
    assert set(first) >= set(convert_register.COLUMNS)


def test_rendered_yaml_round_trips(make_repo: MakeRepo) -> None:
    data = convert(make_repo(), "fixed")
    assert yaml.safe_load(convert_register.render(data)) == data


@pytest.mark.parametrize("case", ["bad-status", "cell-count"])
def test_broken_register_is_rejected(make_repo: MakeRepo, case: str) -> None:
    with pytest.raises(convert_register.RegisterError):
        convert(make_repo(), f"broken/{case}")


def test_repository_register_ids_and_statuses(real_repo: Repo) -> None:
    rows = real_repo.register
    assert sorted(rows) == [f"R-{n:03d}" for n in range(1, 38)]
    pattern = real_repo.pattern("requirement-id-pattern")
    assert all(pattern.fullmatch(i) for i in rows)
