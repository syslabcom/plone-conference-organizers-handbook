"""Adapt source conventions to existing Sphinx directives without changing files."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, assert_never

if TYPE_CHECKING:
    from sphinx.application import Sphinx

from .documents import fixed_content, parse_blocks, parse_page
from .models import Config, Entry, entries


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def render_source(content: str, config: Config, page_id: str = "") -> str:
    """Avoid MyST's note-argument warning and give old notes a stock dropdown."""
    page = parse_page(Entry("", "", "page", "", "written"), content, config)
    fixed = fixed_content(page, config)
    lines = fixed.splitlines(keepends=True)
    blocks = parse_blocks(fixed, config)
    for index, block in reversed(tuple(enumerate(blocks))):
        classes = " ".join(block.classes)
        match block.fields.kind:
            case "lesson":
                if "hb-age-old" in block.classes:
                    opening = [f"{block.fence}{{dropdown}} {block.title}\n", f":class-container: {classes} note\n", ":class-title: admonition-title\n", "\n"]
                else:
                    opening = [f"{block.fence}{{admonition}} {block.title}\n", f":class: {classes} note\n", "\n"]
            case "risk":
                opening = [f"{block.fence}{{admonition}} {block.title}\n", f":class: {classes} warning\n", f":name: {page_id}#risk-{slug(block.title)}\n", "\n"]
            case "thin":
                opening = [f"{block.fence}{{admonition}} {block.title}\n", f":class: {classes} warning\n", f":name: {page_id}#thin-{index + 1}-{slug(block.title)}\n", "\n"]
            case _:
                assert_never(block.fields.kind)
        lines[block.start:block.start + 2] = opening
    return "".join(lines)


def prepare_source(app: Sphinx, docname: str, source: list[str]) -> None:
    root = app.srcdir.parent
    config = Config.load(root)
    catalog = {entry.path: entry.id for entry in entries(root, config)}
    page_id = catalog.get(f"docs/{docname}.md", docname.rsplit("/", 1)[-1])
    source[0] = render_source(source[0], config, page_id)


def setup(app: Sphinx) -> dict[str, bool]:
    _ = app.connect("source-read", prepare_source)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
