# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6"]
# ///
# Run from the repository root: venv/bin/python -m scripts.generate generate
"""Generate registries, repair conventions, or check drift without writing."""

import sys
from pathlib import Path

import yaml

from .documents import fixed_content, read_pages
from .models import Config, ConventionError, entries
from .registries import generated_pages


def run(root: Path, mode: str, selected: tuple[Path, ...] = ()) -> int:
    config = Config.load(root)
    catalog = entries(root, config)
    pages = read_pages(root, catalog, config)
    outputs = generated_pages(pages, catalog, config)
    if mode in {"fix", "check"}:
        selected_paths = {path.resolve() for path in selected}
        outputs.update({
            page.entry.path: fixed_content(page, config)
            for page in pages if not selected_paths or (root / page.entry.path).resolve() in selected_paths
        })
    changed: list[str] = []
    for relative, content in outputs.items():
        path = root / relative
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        changed.append(relative)
        if mode != "check":
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text(content, encoding="utf-8")
    for relative in changed:
        print(f"{'DRIFT' if mode == 'check' else 'WRITE'} {relative}")
    if mode == "check" and changed:
        return 1
    print(f"{'CLEAN' if mode == 'check' else 'GENERATED'}: {len(outputs)} files checked, {len(changed)} changed")
    return 0


def main(argv: tuple[str, ...] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[2]
    if "--root" in args:
        index = args.index("--root")
        if index + 1 >= len(args):
            print("--root requires a directory", file=sys.stderr)
            return 2
        root = Path(args[index + 1]).resolve()
        del args[index:index + 2]
    if not args or args[0] not in {"generate", "fix", "check"} or (args[0] != "fix" and len(args) > 1):
        print("Usage: venv/bin/python -m scripts.generate {generate|fix [PAGE ...]|check} [--root DIR]", file=sys.stderr)
        return 2
    try:
        return run(root, args[0], tuple(Path(arg) if Path(arg).is_absolute() else root / arg for arg in args[1:]))
    except (ConventionError, OSError, yaml.YAMLError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
