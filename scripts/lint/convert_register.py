"""Convert the human Foundation requirements register (Markdown) to data/requirements-register.yml.

The Markdown file stays the human source; the YAML is derived and read by the
lint (rule N02) and the generator. Row IDs ``R01`` become ``R-001`` so they
match ``requirement-id-pattern``. Every column is preserved; ``—`` (no value)
becomes null. ``source-ids`` lists the manifest source IDs that the Source
column resolves to (archived ``BIB/`` paths and live URLs); unresolved
references are kept in ``unresolved-sources``.

Usage:
    venv/bin/python scripts/lint/convert_register.py \
        [--input ../ploneconference/aftermath/documentation/foundation-requirements-register.md] \
        [--output data/requirements-register.yml] [--check]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from hb_common import REGISTER_STATUSES, REPO_ROOT, Repo

DEFAULT_INPUT = REPO_ROOT.parent / "ploneconference/aftermath/documentation/foundation-requirements-register.md"
DEFAULT_OUTPUT = "data/requirements-register.yml"
COLUMNS = ("id", "requirement", "sources", "as-of", "status", "status-note", "source-force", "proposed-badge", "target-chapter")
HEADER_PREFIX = "| ID | Requirement |"
ROW_ID_RE = re.compile(r"^R([0-9]{1,3})$")
BIB_RE = re.compile(r"`BIB/([^`]+)`")
URL_RE = re.compile(r"https://[^\s`;,)]+")
CFP_SET_PHRASE = "CFP set as in R04"
CFP_SET_NOTE_RE = re.compile(r"^`CFP set as in R04` means")
# The register's footnote names the live-only 2020 CFP without spelling out its URL in every row.
CFP_2020_URL = "https://plone.org/news-and-events/events/plone-conferences/online-2020/2020-call-for-proposals"
CFP_2020_PHRASES = ("2020 CFP URL as in R03", "live-only 2020 CFP")
NO_VALUE = "\u2014"
SEP_RE = re.compile(r"\s+\u2014\s+")


class RegisterError(ValueError):
    """The Markdown register does not have the expected table shape."""


def split_row(line: str) -> list[str]:
    cells = line.strip()
    if not (cells.startswith("|") and cells.endswith("|")):
        raise RegisterError(f"table row does not start and end with '|': {line[:60]!r}")
    return [cell.strip() for cell in cells[1:-1].split(" | ")]


def parse_markdown(text: str) -> tuple[list[dict[str, Any]], list[str], str | None]:
    """Return (rows, CFP-set BIB paths from the footnote, document as-of date)."""
    lines = text.splitlines()
    as_of = next((m.group(1) for line in lines if (m := re.match(r"^As of ([0-9]{4}-[0-9]{2}-[0-9]{2})\.$", line))), None)
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith(HEADER_PREFIX))
    except StopIteration as error:
        raise RegisterError("requirements table header not found") from error
    if len(split_row(lines[start])) != len(COLUMNS):
        raise RegisterError("requirements table header does not have nine columns")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines[start + 2 :], start=start + 3):
        if not line.strip():
            break
        cells = split_row(line)
        if len(cells) != len(COLUMNS):
            raise RegisterError(f"line {number}: expected {len(COLUMNS)} cells, found {len(cells)}")
        rows.append(dict(zip(COLUMNS, cells, strict=True)))
    cfp_set = [path for line in lines if CFP_SET_NOTE_RE.match(line) for path in BIB_RE.findall(line)]
    return rows, cfp_set, as_of


def resolve_sources(text: str, cfp_set: list[str], repo: Repo) -> tuple[list[str], list[str]]:
    by_file = {row.get("file", ""): sid for sid, row in repo.manifest.items()}
    by_url = {row.get("url", "").rstrip("/"): sid for sid, row in repo.manifest.items()}
    paths = [p for p in BIB_RE.findall(text)]
    urls = URL_RE.findall(text)
    if CFP_SET_PHRASE in text:
        paths.extend(cfp_set)
        urls.append(CFP_2020_URL)
    if any(phrase in text for phrase in CFP_2020_PHRASES):
        urls.append(CFP_2020_URL)
    found: list[str] = []
    unresolved: list[str] = []
    for path in paths:
        if "\u2026" in path:
            directory = path.split("/")[0]
            matches = [p for p in cfp_set if p.startswith(directory + "/")]
            if matches:
                found.extend(by_file[m] for m in matches if m in by_file)
                continue
        if path in by_file:
            found.append(by_file[path])
        else:
            unresolved.append(f"BIB/{path}")
    for url in urls:
        sid = by_url.get(url.rstrip("/"))
        if sid:
            found.append(sid)
        else:
            unresolved.append(url)
    return sorted(set(found)), list(dict.fromkeys(unresolved))


def target_ids(text: str, repo: Repo) -> tuple[list[str], list[str]]:
    """Map 'Part 2 — Finance; Ticketing and registration' to chapter-list ids by title."""
    titles = {entry.title.casefold(): entry.id for entry in repo.entries}
    found: list[str] = []
    unresolved: list[str] = []
    for chunk in text.split(";"):
        name = SEP_RE.split(chunk.strip())[-1].strip()
        if name.endswith(" playbook"):
            name = "Playbook: " + name.removesuffix(" playbook").strip()
        entry_id = titles.get(name.casefold())
        if entry_id:
            found.append(entry_id)
        elif name:
            unresolved.append(name)
    return list(dict.fromkeys(found)), unresolved


def convert(text: str, repo: Repo, source_name: str) -> dict[str, Any]:
    rows, cfp_set, as_of = parse_markdown(text)
    converted: list[dict[str, Any]] = []
    for row in rows:
        match = ROW_ID_RE.match(row["id"])
        if not match:
            raise RegisterError(f"row id {row['id']!r} is not R<number>")
        if row["status"] not in REGISTER_STATUSES:
            raise RegisterError(f"{row['id']}: status {row['status']!r} is not a register status")
        try:
            row_as_of = dt.date.fromisoformat(row["as-of"])
        except ValueError as error:
            raise RegisterError(f"{row['id']}: as-of {row['as-of']!r} is not an ISO date") from error
        source_ids, unresolved = resolve_sources(row["sources"], cfp_set, repo)
        chapters, unresolved_chapters = target_ids(row["target-chapter"], repo)
        item: dict[str, Any] = {key: (None if row[key] == NO_VALUE else row[key]) for key in COLUMNS}
        item["id"] = f"R-{int(match.group(1)):03d}"
        item["as-of"] = row_as_of
        item["source-ids"] = source_ids
        item["unresolved-sources"] = unresolved
        item["target-chapter-ids"] = chapters
        item["unresolved-target-chapters"] = unresolved_chapters
        converted.append(item)
    ids = [r["id"] for r in converted]
    if len(set(ids)) != len(ids):
        raise RegisterError("duplicate requirement IDs")
    return {
        "source": source_name,
        "as-of": dt.date.fromisoformat(as_of) if as_of else None,
        "rows": converted,
    }


def render(data: dict[str, Any]) -> str:
    header = (
        "# Foundation requirements register, machine-readable.\n"
        "# Generated by scripts/lint/convert_register.py from the Markdown register; do not edit by hand.\n"
        "# Rule N02 reads id, as-of and status. A null value stands for an em dash (no value) in the source.\n"
    )
    return header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10_000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--source-name", default="ploneconference/aftermath/documentation/foundation-requirements-register.md")
    parser.add_argument("--check", action="store_true", help="exit 1 if the output file is out of date")
    args = parser.parse_args(argv)
    repo = Repo(args.root)
    try:
        rendered = render(convert(args.input.read_text(encoding="utf-8"), repo, args.source_name))
    except RegisterError as error:
        print(f"convert_register: {error}", file=sys.stderr)
        return 2
    output = repo.path(args.output)
    if args.check:
        current = output.read_text(encoding="utf-8") if output.is_file() else ""
        if current != rendered:
            print(f"convert_register: {args.output} is out of date", file=sys.stderr)
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"convert_register: wrote {len(yaml.safe_load(rendered)['rows'])} rows to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
