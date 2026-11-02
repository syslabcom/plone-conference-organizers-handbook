# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6"]
# ///
# How to run: venv/bin/python scripts/evidence/build_evidence.py [--check]
"""Generate Part 5 evidence pages, or report drift without writing."""

from __future__ import annotations

import sys
from pathlib import Path

# Support both direct execution and package imports without changing other tooling.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.evidence.models import PAGE_IDS, InputError, load
from scripts.evidence.render import bibliography, conference_index, conference_table, costs, ledger


def build(root: Path, *, check: bool = False) -> int:
    """Only the five chapter-list-owned outputs may be written."""
    evidence = load(root)
    renderers = (conference_index, conference_table, costs, bibliography, ledger)
    drift: list[str] = []
    for page_id, render in zip(PAGE_IDS, renderers, strict=True):
        page = evidence.page(page_id)
        path = root / page.path
        content = render(evidence)
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                drift.append(page.path)
                print(f"DRIFT {page.path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text(content, encoding="utf-8")
            print(f"WROTE {page.path}")
    held = sum(source.held for source in evidence.sources)
    print(f"Sources: {len(evidence.sources) - held} rendered, {held} held back; " +
          f"ledger: {len(evidence.lessons)}; conference years: 24; " +
          f"table evidence: {len(evidence.placed('conference-data-table'))}; " +
          f"cost rows: {len(evidence.placed('cost-benchmarks'))}")
    if check and not drift:
        print("PASS evidence pages match regeneration")
    return int(bool(drift))


def main(argv: list[str] | None = None) -> int:
    """Keep this two-option CLI dependency-free beyond the repo's PyYAML."""
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[2]
    check = "--check" in args
    if check:
        args.remove("--check")
    if "--root" in args:
        position = args.index("--root")
        if position + 1 >= len(args):
            raise InputError("--root needs a repository path")
        root = Path(args[position + 1]).resolve()
        del args[position:position + 2]
    if args in (["--help"], ["-h"]):
        print("Usage: build_evidence.py [--check] [--root PATH]")
        return 0
    if args:
        raise InputError(f"Unknown arguments: {args}")
    return build(root, check=check)


if __name__ == "__main__":
    sys.exit(main())
