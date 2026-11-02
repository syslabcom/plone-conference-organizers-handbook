"""Shared fixtures for the gate tests.

``tests/fixtures/base/`` is the fixed tree: the smallest handbook in which
every gate passes. ``tests/fixtures/<gate>/broken/<case>/`` and
``tests/fixtures/<gate>/fixed/`` are overlays copied on top of the base, each
changing as little as possible. A broken case must fail with exactly the rule
codes its test names.
"""

from __future__ import annotations

import datetime as dt
import os
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lint"))

from hb_common import Repo  # noqa: E402

AS_OF = dt.date(2026, 11, 2)  # the fixture lint date; fixtures are dated against it

MakeRepo = Callable[..., Repo]


def broken_cases(gate: str) -> list[str]:
    folder = FIXTURES / gate / "broken"
    return sorted(p.name for p in folder.iterdir() if p.is_dir()) if folder.is_dir() else []


@pytest.fixture
def make_repo(tmp_path: Path) -> MakeRepo:
    """Build a fixture tree: the base plus overlays such as ``g5/broken/l05-title``."""

    def build(*overlays: str) -> Repo:
        root = tmp_path / "repo"
        shutil.copytree(FIXTURES / "base", root)
        for overlay in overlays:
            source = FIXTURES / overlay
            assert source.is_dir(), f"missing fixture overlay {overlay}"
            shutil.copytree(source, root, dirs_exist_ok=True)
        return Repo(root)

    return build


@pytest.fixture(scope="session")
def real_repo() -> Repo:
    """The repository under test; HANDBOOK_ROOT points it at another tree (used by the xfail proof)."""
    return Repo(Path(os.environ.get("HANDBOOK_ROOT", REPO_ROOT)))


def case_codes(case: str) -> set[str]:
    """The rule codes a broken case is named after: ``l05-title`` -> {"L05"}."""
    return {case.split("-", 1)[0].upper()}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Tests that judge the repository's own content carry the ``repo`` marker.

    ``pytest -m "not repo"`` runs only the fixture proofs of the gates;
    plain ``pytest`` (CI) runs both.
    """
    for item in items:
        if "real_repo" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.repo)
