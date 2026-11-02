import shutil
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.generate.documents import parse_page
from scripts.generate.models import Config, Entry
from scripts.generate.registries import generated_pages, lesson_index

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "scripts/generate/fixtures/chapter.md"
ENTRY = Entry("fixture", "Synthetic chapter", "chapter", "docs/chapter.md", "written")


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    (tmp_path / "docs/spec").mkdir(parents=True)
    _ = shutil.copyfile(ROOT / "handbook-config.yml", tmp_path / "handbook-config.yml")
    _ = shutil.copyfile(FIXTURE, tmp_path / "docs/chapter.md")
    row = {"id": ENTRY.id, "title": ENTRY.title, "kind": ENTRY.kind, "path": ENTRY.path, "status": ENTRY.status}
    _ = (tmp_path / "docs/spec/chapter-list.yml").write_text(yaml.safe_dump({"entries": [row]}))
    return tmp_path


def cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "scripts.generate", *args, "--root", str(root)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)


def test_thin_registry_preserves_needs_when_generated() -> None:
    # Given a chapter containing a thin marker.
    page = parse_page(ENTRY, FIXTURE.read_text(), Config())
    marker = next(block for block in page.blocks if block.fields.kind == "thin")
    # When rendering the generated pages.
    output = generated_pages((page,), (ENTRY,), Config())
    # Then the contribution request appears under its kind.
    assert marker.fields.values["needs"] in output["docs/generated/thin-registry.md"]
    assert "## Gap" in output["docs/generated/thin-registry.md"]


def test_risk_register_aggregates_risk_when_generated() -> None:
    # Given the fixture chapter's low-likelihood, high-impact risk.
    page = parse_page(ENTRY, FIXTURE.read_text(), Config())
    # When rendering the risk register.
    output = generated_pages((page,), (ENTRY,), Config())["docs/generated/risk-register.md"]
    # Then the risk is linked to its section with the computed score.
    assert "{ref}`Venue becomes unavailable <fixture#risk-venue-becomes-unavailable>`" in output
    assert "| low | high | 3 |" in output


def test_repairs_title_and_classes_when_fix_runs(repository: Path) -> None:
    # Given incorrect computed fields but an intact provenance strip and body.
    path = repository / "docs/chapter.md"
    original = path.read_text()
    _ = path.write_text(original.replace("[specific · 2012 · Arnhem · 14 y] stale-prone", "wrong badge").replace("hb-age-old hb-stale-prone", "hb-age-recent extra-class"))
    # When invoking the public fix command for that page.
    result = cli(repository, "fix", "docs/chapter.md")
    # Then only the drifted title and class lines return to the expected document.
    assert result.returncode == 0, result.stderr
    assert path.read_text() == original


def test_check_detects_drift_when_generated_page_is_doctored(repository: Path) -> None:
    # Given generated pages with a manually doctored risk register.
    assert cli(repository, "generate").returncode == 0
    path = repository / "docs/generated/risk-register.md"
    _ = path.write_text(path.read_text() + "Unwanted manual edit.\n")
    before = path.read_bytes()
    # When invoking the CI check command.
    result = cli(repository, "check")
    # Then it exits nonzero, names the drift, and leaves the file untouched.
    assert result.returncode == 1
    assert "DRIFT docs/generated/risk-register.md" in result.stdout
    assert path.read_bytes() == before


def test_check_is_clean_when_regeneration_restores_page(repository: Path) -> None:
    # Given a doctored file that regeneration has restored.
    assert cli(repository, "generate").returncode == 0
    path = repository / "docs/generated/coverage-map.md"
    _ = path.write_text("doctored\n")
    assert cli(repository, "generate").returncode == 0
    # When invoking the CI check command.
    result = cli(repository, "check")
    # Then the exit code certifies deterministic regeneration.
    assert result.returncode == 0, result.stdout + result.stderr


def test_decision_register_extracts_continuation_deadline_when_generated() -> None:
    # Given a decision with indented guidance and a sub-bullet.
    page = parse_page(ENTRY, FIXTURE.read_text(), Config())
    # When rendering the decision register.
    output = generated_pages((page,), (ENTRY,), Config())["docs/generated/decision-register.md"]
    # Then it has one decision and the deadline from the continuation line.
    assert output.count("Which fallback venue should the team shortlist?") == 1
    assert "| OPTION | Which fallback venue should the team shortlist? | T-6m |" in output


def test_coverage_counts_content_when_chapter_is_present() -> None:
    # Given an authored chapter and an unwritten planned page.
    page = parse_page(ENTRY, FIXTURE.read_text(), Config())
    planned = Entry("future", "Future", "chapter", "docs/future.md", "planned")
    # When rendering coverage.
    output = generated_pages((page,), (ENTRY, planned), Config())["docs/generated/coverage-map.md"]
    # Then maturity, per-kind counts and zero-count areas remain visible.
    assert "| fixture | written | draft | 1 | 0 | 0 | 1 | 1 | 1 |" in output
    assert "| future | planned |  | 0 | 0 | 0 | 0 | 0 | 0 |" in output
    assert "| accessibility | 1 |" in output
    assert "| hybrid-online | 0 |" in output


def test_lesson_index_orders_general_before_specific_when_source_order_differs() -> None:
    # Given reversed input block order.
    from dataclasses import replace
    page = parse_page(ENTRY, FIXTURE.read_text(), Config())
    reversed_page = replace(page, blocks=tuple(reversed(page.blocks)))
    # When rendering the lesson index.
    output = lesson_index((reversed_page,), Config())
    # Then the general lesson still precedes the dated case note.
    assert output.index("general") < output.index("specific")


def test_cli_reports_error_when_source_is_invalid(repository: Path) -> None:
    # Given a specific lesson without its required year.
    path = repository / "docs/chapter.md"
    _ = path.write_text(path.read_text().replace(" | year: 2012", ""))
    # When generating via the public CLI.
    result = cli(repository, "generate")
    # Then it reports the rule and source path before writing any output.
    assert result.returncode == 2
    assert "L01: docs/chapter.md:" in result.stderr
    assert not (repository / "docs/generated").exists()


def test_sphinx_renders_closed_old_lesson_when_building_real_fixture(repository: Path) -> None:
    # Given the actual project configuration, CSS, fixture and generated pages.
    docs = repository / "docs"
    (repository / "scripts").mkdir()
    _ = shutil.copytree(ROOT / "scripts/generate", repository / "scripts/generate", ignore=shutil.ignore_patterns("__pycache__", "tests"))
    _ = shutil.copyfile(ROOT / "docs/conf.py", docs / "conf.py")
    (docs / "_static").mkdir()
    (docs / "_templates").mkdir()
    _ = shutil.copyfile(ROOT / "docs/_static/hb.css", docs / "_static/hb.css")
    names = ("lesson-index", "risk-register", "thin-registry", "decision-register", "coverage-map")
    _ = (docs / "index.md").write_text("# Fixture handbook\n\n```{toctree}\n\nchapter\n" + "\n".join(f"generated/{name}" for name in names) + "\n```\n")
    assert cli(repository, "generate").returncode == 0
    original = (docs / "chapter.md").read_bytes()
    # When building the real Sphinx surface with warnings as errors.
    result = subprocess.run([sys.executable, "-m", "sphinx", "-b", "html", "-W", "--keep-going", str(docs), str(repository / "html")], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
    # Then the old lesson is a closed stock dropdown with its exact badge heading.
    assert result.returncode == 0, result.stdout + result.stderr
    rendered = (repository / "html/chapter.html").read_text()
    details = re.search(r"<details\b([^>]*hb-age-old[^>]*)>(.*?)</details>", rendered, re.DOTALL)
    assert details is not None
    assert "open=" not in details[1]
    assert re.search(r"<summary\b.*?\[specific · 2012 · Arnhem · 14 y\] stale-prone.*?</summary>", details[2], re.DOTALL)
    assert "hb.css" in rendered
    assert (docs / "chapter.md").read_bytes() == original
    assert all((repository / f"html/generated/{name}.html").is_file() for name in names)
