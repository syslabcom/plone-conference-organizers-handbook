"""Line-based MyST Markdown parsing for the lint gates.

Tracks fences from the top of the file (conventions.md, section 2.3), finds
ATX headings outside fences, splits sections, and recognizes the managed
lesson, thin and risk admonition blocks (conventions.md, section 2).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

FENCE_OPEN_RE = re.compile(r"^( {0,3})(`{3,}|~{3,}|:{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")
DIRECTIVE_RE = re.compile(r"^\{([A-Za-z0-9_-]+)\}[ \t]*(.*)$")
OPTION_RE = re.compile(r"^:([A-Za-z0-9_-]+):[ \t]*(.*)$")
LIST_ITEM_RE = re.compile(r"^([ \t]*)([-*+]|[0-9]+[.)])[ \t]+")
FIELD_SEP = " | "
FIELD_KEY_RE = re.compile(r"[a-z][a-z-]*")
BlockKind = Literal["lesson", "thin", "risk"]
MANAGED_KINDS = ("lesson", "thin", "risk")
KIND_CLASS: dict[str, BlockKind] = {"hb-lesson": "lesson", "hb-thin": "thin", "hb-risk": "risk"}
ADMONITIONS = frozenset(
    {
        "admonition", "attention", "caution", "danger", "error", "hint",
        "important", "note", "seealso", "tip", "todo", "warning",
    }
)


@dataclass(frozen=True, slots=True)
class Heading:
    level: int
    text: str
    index: int  # 0-based line index


@dataclass(frozen=True, slots=True)
class Fence:
    start: int  # line index of the opening fence
    end: int  # line index of the closing fence (or last line when unclosed)
    char: str
    length: int
    info: str
    closed: bool

    @property
    def directive(self) -> str | None:
        match = DIRECTIVE_RE.match(self.info.strip())
        return match.group(1) if match else None

    @property
    def argument(self) -> str:
        match = DIRECTIVE_RE.match(self.info.strip())
        return match.group(2).strip() if match else ""


@dataclass(slots=True)
class Block:
    """A managed block candidate: a top-level directive fence that looks like a lesson, thin or risk."""

    fence: Fence
    directive: str
    title: str
    options: list[tuple[int, str, str]]  # (index, name, value)
    classes: tuple[str, ...]
    field_index: int | None
    field_line: str | None
    blank_after_field: bool
    body: list[str]
    section: str | None = None
    kind: str | None = None  # parsed first segment of the field line
    fields: dict[str, str] = field(default_factory=dict)
    parse_error: str | None = None

    @property
    def line(self) -> int:
        return self.fence.start + 1

    @property
    def class_kinds(self) -> set[BlockKind]:
        return {KIND_CLASS[c] for c in self.classes if c in KIND_CLASS}


@dataclass(slots=True)
class Section:
    heading: Heading
    start: int  # index of the heading line
    end: int  # exclusive

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.heading.text.lower()).strip("-")


@dataclass(slots=True)
class Page:
    path: Path
    lines: list[str]
    front_matter: str | None
    front_matter_error: str | None
    body_start: int
    fences: list[Fence]
    in_fence: list[bool]
    headings: list[Heading]
    blocks: list[Block]

    def sections(self, level: int = 2) -> list[Section]:
        marks = [h for h in self.headings if h.level <= level]
        result: list[Section] = []
        for pos, heading in enumerate(marks):
            if heading.level != level:
                continue
            end = len(self.lines)
            for later in marks[pos + 1 :]:
                end = later.index
                break
            result.append(Section(heading, heading.index, end))
        return result

    def section_at(self, index: int) -> Section | None:
        for section in self.sections():
            if section.start <= index < section.end:
                return section
        return None

    def section_by_slug(self, slug: str) -> Section | None:
        return next((s for s in self.sections() if s.slug == slug), None)


def parse_field_line(line: str) -> tuple[str, dict[str, str]]:
    """The reference field-line parser of conventions.md, section 2.2."""
    parts = line.strip().split(FIELD_SEP)
    kind, fields = parts[0].strip(), {}
    for part in parts[1:]:
        key, sep, value = part.partition(":")
        key, value = key.strip(), value.strip()
        if not (sep and FIELD_KEY_RE.fullmatch(key) and value):
            raise ValueError(f"bad field segment: {part!r}")
        if key in fields:
            raise ValueError(f"duplicate key: {key}")
        fields[key] = value
    return kind, fields


def split_list(value: str) -> list[str]:
    """Comma-separated list value; empty items are kept so callers can report them."""
    return [item.strip() for item in value.split(",")]


def split_front_matter(lines: list[str]) -> tuple[str | None, int, str | None]:
    """Return (front matter text, first body line index, error)."""
    if not lines or lines[0].rstrip() != "---":
        return None, 0, None
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return "\n".join(lines[1:index]), index + 1, None
    return None, 0, "front matter block is not closed"


def find_fences(lines: list[str], start: int) -> list[Fence]:
    """Top-level fences only; content of a fence is opaque until its closing fence."""
    fences: list[Fence] = []
    index = start
    while index < len(lines):
        match = FENCE_OPEN_RE.match(lines[index])
        if not match or (match.group(2)[0] == "`" and "`" in match.group(3)):
            index += 1
            continue
        char, length, info = match.group(2)[0], len(match.group(2)), match.group(3)
        close_re = re.compile(rf"^ {{0,3}}{re.escape(char)}{{{length},}}[ \t]*$")
        end = next((j for j in range(index + 1, len(lines)) if close_re.match(lines[j])), None)
        if end is None:
            fences.append(Fence(index, len(lines) - 1, char, length, info, closed=False))
            break
        fences.append(Fence(index, end, char, length, info, closed=True))
        index = end + 1
    return fences


def _block_from_fence(lines: list[str], fence: Fence) -> Block | None:
    directive = fence.directive
    if directive is None:
        return None
    index = fence.start + 1
    options: list[tuple[int, str, str]] = []
    while index < fence.end and (match := OPTION_RE.match(lines[index])):
        options.append((index, match.group(1), match.group(2).strip()))
        index += 1
    while index < fence.end and not lines[index].strip():
        index += 1
    field_index = index if index < fence.end else None
    field_line = lines[index] if field_index is not None else None
    classes: tuple[str, ...] = ()
    for _i, name, value in options:
        if name == "class":
            classes = tuple(value.split())
    first_segment = field_line.strip().split(FIELD_SEP)[0].strip() if field_line else ""
    managed = any(c in KIND_CLASS for c in classes) or first_segment in MANAGED_KINDS
    if not managed:
        return None
    blank_after = (
        field_index is not None
        and (field_index + 1 >= fence.end or not lines[field_index + 1].strip())
    )
    body_start = (field_index + 1) if field_index is not None else fence.end
    return Block(
        fence=fence,
        directive=directive,
        title=fence.argument,
        options=options,
        classes=classes,
        field_index=field_index,
        field_line=field_line,
        blank_after_field=blank_after,
        body=lines[body_start : fence.end],
    )


def parse_text(path: Path, text: str) -> Page:
    lines = text.splitlines()
    front_matter, body_start, fm_error = split_front_matter(lines)
    fences = find_fences(lines, body_start)
    in_fence = [False] * len(lines)
    for fence in fences:
        for j in range(fence.start, fence.end + 1):
            in_fence[j] = True
    headings: list[Heading] = []
    for index in range(body_start, len(lines)):
        if in_fence[index]:
            continue
        match = HEADING_RE.match(lines[index])
        if match:
            headings.append(Heading(len(match.group(1)), match.group(2).strip(), index))
    page = Page(path, lines, front_matter, fm_error, body_start, fences, in_fence, headings, [])
    for fence in fences:
        if fence.char != "`":
            continue
        block = _block_from_fence(lines, fence)
        if block is None:
            continue
        section = page.section_at(fence.start)
        block.section = section.heading.text if section else None
        if block.field_line is not None:
            try:
                block.kind, block.fields = parse_field_line(block.field_line)
            except ValueError as error:
                block.kind = block.field_line.strip().split(FIELD_SEP)[0].strip()
                block.parse_error = str(error)
        page.blocks.append(block)
    return page


def parse_page(path: Path) -> Page:
    return parse_text(path, path.read_text(encoding="utf-8"))


def colon_managed_fences(page: Page) -> list[Fence]:
    """Colon fences that carry a managed block (rule B06)."""
    found: list[Fence] = []
    for fence in page.fences:
        if fence.char != ":" or fence.directive is None:
            continue
        window = page.lines[fence.start + 1 : min(fence.end, fence.start + 6)]
        text = "\n".join(window)
        if re.search(r"\bhb-(lesson|thin|risk)\b", text) or re.search(
            r"^\s*(lesson|thin|risk) \| ", text, re.MULTILINE
        ):
            found.append(fence)
    return found


def list_items(lines: list[str], start: int, end: int, in_fence: list[bool]) -> list[tuple[int, int, int]]:
    """List items in a range as (start index, end index exclusive, indent)."""
    items: list[tuple[int, int, int]] = []
    for index in range(start, end):
        if in_fence[index]:
            continue
        match = LIST_ITEM_RE.match(lines[index])
        if match:
            items.append((index, end, len(match.group(1).expandtabs(4))))
    result: list[tuple[int, int, int]] = []
    for pos, (index, _end, indent) in enumerate(items):
        stop = end
        for later, _e, later_indent in items[pos + 1 :]:
            if later_indent <= indent:
                stop = later
                break
        # A top-level item also stops at the first non-indented, non-blank, non-list line.
        for j in range(index + 1, stop):
            line = lines[j]
            if line.strip() and not in_fence[j] and not line[:1].isspace() and not LIST_ITEM_RE.match(line):
                stop = j
                break
        result.append((index, stop, indent))
    return result


def strip_list_marker(line: str) -> str:
    match = LIST_ITEM_RE.match(line)
    return line[match.end() :] if match else line.strip()


def content_lines(page: Page, start: int, end: int) -> list[tuple[int, str]]:
    """Non-blank lines in a range that are not MyST comments."""
    return [
        (j, page.lines[j])
        for j in range(start, end)
        if page.lines[j].strip() and not page.lines[j].lstrip().startswith("%")
    ]


def prose_lines(page: Page) -> list[int]:
    """Body line indices that are prose: outside fences, or inside an admonition directive.

    Code blocks and other directives (for example a ```` ```markdown ```` example) are not prose.
    """
    admonition = {
        j
        for fence in page.fences
        if fence.directive in ADMONITIONS
        for j in range(fence.start, fence.end)
    }
    return [
        j for j in range(page.body_start, len(page.lines))
        if not page.in_fence[j] or j in admonition
    ]
