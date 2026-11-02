"""Exercise evidence views through real, isolated input trees and CLI runs."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.evidence.models import PARSERS, InputError, load
from scripts.evidence.render import bibliography, conference_table

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CLI = ROOT / "scripts/evidence/build_evidence.py"


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    _ = shutil.copytree(HERE / "fixtures", tmp_path, dirs_exist_ok=True)
    return tmp_path


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "--root", str(root), *args],
        capture_output=True, text=True, check=False,
    )


def test_outputs_when_fixture_inputs_are_rendered(repository: Path) -> None:
    # Given: a fixture with public, held, internal, conflicting and missing evidence.
    expected = HERE / "golden"
    # When: the real CLI generates its pages.
    result = run(repository)
    # Then: every generated document matches the reviewed golden artifact.
    assert result.returncode == 0, result.stderr
    for page in expected.glob("*.md"):
        assert (repository / "docs/evidence" / page.name).read_bytes() == page.read_bytes()


def test_check_fails_when_page_is_doctored(repository: Path) -> None:
    # Given: generated output whose bibliography is subsequently edited.
    assert run(repository).returncode == 0
    page = repository / "docs/evidence/source-bibliography.md"
    _ = page.write_text("doctored\n", encoding="utf-8")
    # When: drift mode compares it without writing.
    result = run(repository, "--check")
    # Then: it rejects drift and preserves the doctored file.
    assert result.returncode == 1
    assert "DRIFT docs/evidence/source-bibliography.md" in result.stdout
    assert page.read_text(encoding="utf-8") == "doctored\n"


def test_check_passes_when_doctored_output_is_regenerated(repository: Path) -> None:
    # Given: a doctored page repaired by normal generation.
    page = repository / "docs/evidence/source-bibliography.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    _ = page.write_text("doctored\n", encoding="utf-8")
    assert run(repository).returncode == 0
    # When: drift mode checks repaired output.
    result = run(repository, "--check")
    # Then: no output differs.
    assert result.returncode == 0, result.stdout + result.stderr


def test_private_archive_paths_are_absent_when_sources_are_held(repository: Path) -> None:
    # Given: one explicitly excluded source and an internal source without an audit.
    evidence = load(repository)
    # When: bibliography metadata is rendered.
    output = bibliography(evidence)
    # Then: neither held archive filename nor its original URL is published.
    for forbidden in ("private.html", "internal-note.md", "https://example.org/private"):
        assert forbidden not in output
    assert "S002" in output and "S098" in output


def test_archive_note_is_published_when_audit_records_one(repository: Path) -> None:
    # Given: an audit row whose notes column records a redaction for a rendered source.
    audit = repository / "data/sources/archive-audit.csv"
    with audit.open(encoding="utf-8", newline="") as handle:
        rows = [{**row, "notes": "personal data redacted by marker replacement" if row["source_id"] == "S001" else ""}
                for row in csv.DictReader(handle)]
    with audit.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*rows[0].keys()])
        writer.writeheader()
        writer.writerows(rows)
    # When: bibliography metadata is rendered.
    output = bibliography(load(repository))
    # Then: the note follows the rendered entry, and the held entry carries none.
    entry = output.split("(s001)=", 1)[1].split("(s002)=", 1)[0]
    assert "Archive note: personal data redacted by marker replacement." in entry
    assert output.count("Archive note:") == 1


def test_output_is_stable_when_input_order_changes(repository: Path) -> None:
    # Given: output generated from the fixture order.
    assert run(repository).returncode == 0
    manifest = repository / "data/sources/manifest.csv"
    with manifest.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    assert fields is not None
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(reversed(rows))
    ledger = repository / "data/ledger/example.yml"
    document = PARSERS.ledger(ledger.read_text(encoding="utf-8"))
    document["rows"].reverse()
    _ = ledger.write_text(yaml.safe_dump(document), encoding="utf-8")
    # When: drift mode processes the reordered inputs.
    result = run(repository, "--check")
    # Then: ordering has not changed any output bytes.
    assert result.returncode == 0, result.stdout + result.stderr


def test_input_is_rejected_when_json_and_csv_disagree(repository: Path) -> None:
    # Given: an additional JSON source missing from CSV.
    path = repository / "data/sources/manifest.json"
    document = PARSERS.manifest(path.read_text(encoding="utf-8"))
    document["sources"].append({"source_id": "S999"})
    _ = path.write_text(json.dumps(document), encoding="utf-8")
    # When/Then: boundary parsing rejects the inconsistent manifests.
    with pytest.raises(InputError, match="match the combined JSON blocks"):
        _ = load(repository)


def test_population_labels_survive_when_counts_conflict(repository: Path) -> None:
    # Given: a conference count, sprint count and conflicting attendance count.
    evidence = load(repository)
    # When: the conference table is rendered.
    output = conference_table(evidence)
    # Then: each population remains independently cited, including the conflict.
    row = next(line for line in output.splitlines() if line.startswith("| 2006"))
    assert "about 350 attendees[^L-1001]" in row
    assert "360 attendees[^L-1002]" in row
    assert "50 sprinters[^L-1003]" in row
