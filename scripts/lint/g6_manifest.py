"""Gate G6: source manifest integrity (ledger-schema.md, LD06).

Checks that every manifest row names an existing file with a matching
sha256, that every source ID cited anywhere (ledger rows, lesson blocks,
page prose, the requirements register) exists in the manifest, and that the
generated source bibliography will list every manifest entry.

Codes: M01 manifest row invalid; M02 file missing; M03 sha256 mismatch;
M04 cited source ID not in the manifest; M05 bibliography coverage.

Usage: venv/bin/python scripts/lint/g6_manifest.py [--root PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from hb_common import REPO_ROOT, Finding, Repo, rel, report
from hb_markdown import parse_page, prose_lines, split_list

REQUIRED_COLUMNS = ("source_id", "file", "sha256")
BIBLIOGRAPHY_ID = "source-bibliography"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_findings(repo: Repo) -> list[Finding]:
    manifest_path = repo.config_path("source-manifest")
    where = rel(repo, manifest_path)
    if not manifest_path.is_file():
        return [Finding("M01", where, 0, "source manifest is missing")]
    rows = repo.manifest_rows
    findings: list[Finding] = []
    if rows and any(column not in rows[0] for column in REQUIRED_COLUMNS):
        return [Finding("M01", where, 1, f"manifest needs the columns {', '.join(REQUIRED_COLUMNS)}")]
    pattern = repo.pattern("source-id-pattern")
    seen: set[str] = set()
    base = manifest_path.parent
    for line, row in enumerate(rows, start=2):
        source_id = row.get("source_id") or ""
        if not pattern.fullmatch(source_id):
            findings.append(Finding("M01", where, line, f"source_id {source_id!r} does not match {pattern.pattern}"))
        if source_id in seen:
            findings.append(Finding("M01", where, line, f"source_id {source_id} is duplicated"))
        seen.add(source_id)
        file = (row.get("file") or "").strip()
        target = (base / file).resolve()
        if not file or base.resolve() not in target.parents or not target.is_file():
            findings.append(Finding("M02", where, line, f"{source_id}: file {file!r} does not exist under {rel(repo, base)}"))
            continue
        actual = sha256(target)
        if actual != (row.get("sha256") or "").strip().lower():
            findings.append(Finding("M03", where, line, f"{source_id}: sha256 of {file} is {actual}, manifest says {row.get('sha256')}"))
    return findings


def cited_sources(repo: Repo) -> list[tuple[str, str, int]]:
    """Every (source ID, path, line) cited in ledger rows, lessons, pages and the register."""
    cited: list[tuple[str, str, int]] = []
    for path, data, _error in repo.ledger_docs:
        rows = data.get("rows") if isinstance(data, dict) else None
        for row in rows if isinstance(rows, list) else []:
            if isinstance(row, dict) and isinstance(row.get("source_id"), str):
                cited.append((row["source_id"], rel(repo, path), 0))
    token = repo.token_regex("source-id-pattern")
    for path in repo.markdown_pages():
        page = parse_page(path)
        for block in page.blocks:
            for source in split_list(block.fields.get("source", "")):
                if source:
                    cited.append((source, rel(repo, path), block.line))
        for index in prose_lines(page):
            for match in token.finditer(page.lines[index]):
                cited.append((match.group(0), rel(repo, path), index + 1))
    register_path = rel(repo, repo.config_path("requirements-register"))
    for row in repo.register.values():
        for source in row.get("source-ids") or []:
            cited.append((str(source), register_path, 0))
    return cited


def bibliography_findings(repo: Repo) -> list[Finding]:
    chapter_list = repo.config["paths"]["chapter-list"]
    entry = repo.entries_by_id.get(BIBLIOGRAPHY_ID)
    if entry is None or entry.kind != "generated":
        return [Finding("M05", chapter_list, 0, f"the chapter list needs a generated entry {BIBLIOGRAPHY_ID!r} that lists every manifest source")]
    page = repo.path(entry.path)
    if not entry.written or not page.is_file():
        return []
    text = page.read_text(encoding="utf-8")
    return [
        Finding("M05", entry.path, 0, f"{source_id} is in the manifest but missing from the bibliography")
        for source_id in sorted(repo.manifest)
        if source_id not in text
    ]


def check(repo: Repo) -> list[Finding]:
    findings = manifest_findings(repo)
    known = set(repo.manifest)
    reported: set[tuple[str, str]] = set()
    for source_id, path, line in cited_sources(repo):
        if source_id not in known and (source_id, path) not in reported:
            reported.add((source_id, path))
            findings.append(Finding("M04", path, line, f"cited source {source_id} is not in the source manifest"))
    return findings + bibliography_findings(repo)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    return report(check(Repo(args.root)), "G6 manifest integrity")


if __name__ == "__main__":
    sys.exit(main())
