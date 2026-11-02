"""Fence-aware extraction and minimally invasive lesson repair."""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final, assert_never

from .fields import parse_field_line
from .lessons import lesson_classes, lesson_title, ordered_classes
from .models import DEFAULT_CONFIG, Block, Config, ConventionError, Decision, Entry, Page, mapping, parse_yaml, text

FENCE: Final = re.compile(r"^ {0,3}(`{3,}|~{3,}|:{3,})(.*)$")
HEADING: Final = re.compile(r"^##\s+(?:[0-9]+[.)]?\s+)?(.+?)(?:\s+#+)?$")
BADGES: Final = {
    "MUST": r"^\{bdg-danger\}`MUST` \(req: R-[0-9]{3}; as-of: [0-9]{4}-[0-9]{2}-[0-9]{2}\)",
    "DEFAULT": r"^\{bdg-primary\}`DEFAULT` \(basis: L-[0-9]{4}(, L-[0-9]{4})+\)",
    "OPTION": r"^\{bdg-secondary\}`OPTION`",
}


def top_level_lines(lines: list[str]) -> Iterator[tuple[int, str, int | None]]:
    """Skip complete outer fences, including examples containing managed syntax."""
    index = 0
    while index < len(lines):
        found = FENCE.match(lines[index])
        if found:
            fence = found[1]
            closing = re.compile(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$")
            end = index + 1
            while end < len(lines) and not closing.fullmatch(lines[end]):
                end += 1
            yield index, lines[index], end if end < len(lines) else None
            index = end + 1
        else:
            yield index, lines[index], None
            index += 1


def parse_blocks(content: str, config: Config = DEFAULT_CONFIG) -> tuple[Block, ...]:
    lines = content.splitlines()
    section = ""
    result: list[Block] = []
    for index, line, end in top_level_lines(lines):
        heading = HEADING.fullmatch(line)
        if heading:
            section = heading[1].strip().casefold()
        opening = FENCE.match(line)
        if not opening or not re.match(r"\{(?:note|warning)\}", opening[2]):
            continue
        class_line = lines[index + 1] if index + 1 < len(lines) else ""
        option_end = index + 1
        option_lines: list[str] = []
        while option_end < len(lines) and lines[option_end].startswith(":"):
            option_lines.append(lines[option_end])
            option_end += 1
        managed_options = [option for option in option_lines if option.startswith(":class:") and re.search(r"\bhb-(lesson|thin|risk)\b", option)]
        if managed_options and (len(option_lines) != 1 or not class_line.startswith(":class:")):
            raise ConventionError("B04", "only an immediate class option is allowed")
        tokens = tuple(class_line.removeprefix(":class:").split())
        kinds = [kind for kind in ("lesson", "thin", "risk") if f"hb-{kind}" in tokens]
        if not kinds:
            continue
        if len(kinds) != 1 or not class_line.startswith(":class:"):
            raise ConventionError("B04", f"ambiguous classes at line {index + 1}")
        if not opening[1].startswith("`"):
            raise ConventionError("B06", "managed blocks require backtick fences")
        if end is None or lines[end].strip() != opening[1]:
            raise ConventionError("B01", "managed closing fence must match opening length")
        body_start = index + 2
        while body_start < end and not lines[body_start].strip():
            body_start += 1
        if body_start >= end:
            raise ConventionError("B01", "missing field line")
        if lines[body_start].startswith(":"):
            raise ConventionError("B04", "only the class option is allowed")
        fields = parse_field_line(lines[body_start], config)
        if f"hb-{fields.kind}" not in tokens:
            raise ConventionError("B02", "field kind differs from class-implied kind")
        directive, _, title = opening[2].partition(" ")
        expected = "{note}" if fields.kind == "lesson" else "{warning}"
        if directive != expected:
            raise ConventionError("B03", "directive does not match block kind")
        if body_start + 1 >= end or lines[body_start + 1].strip():
            raise ConventionError("B01", "a blank line must follow the field line")
        if fields.kind != "lesson" and (not 1 <= len(title) <= 80 or "`" in title):
            raise ConventionError("B01", "author-written title must be 1 to 80 characters without backticks")
        result.append(Block(index, end, opening[1], title, tokens, fields, section))
    return tuple(result)


def parse_decisions(content: str) -> tuple[Decision, ...]:
    section = ""
    bullets: list[list[str]] = []
    for _, line, _end in top_level_lines(content.splitlines()):
        if FENCE.match(line):
            continue
        heading = HEADING.fullmatch(line)
        if heading:
            section = heading[1].strip().casefold()
        if section != "decisions you must make":
            continue
        bullet = re.match(r"^[-+*] (.+)$", line)
        if bullet:
            bullets.append([bullet[1]])
        elif bullets and (line.startswith("  ") or not line.strip()):
            bullets[-1].append(line.strip())
    result: list[Decision] = []
    for lines in bullets:
        item = " ".join(lines)
        levels = [level for level, pattern in BADGES.items() if re.match(pattern, item)]
        question = re.search(r"\*\*(.+?)\*\*", item)
        if len(levels) != 1 or question is None:
            raise ConventionError("N01", "decision requires a leading badge and bold decision")
        deadline = re.search(r"\(decide-by: (T-[0-9]+[dwm])\)", item)
        result.append(Decision(levels[0], question[1], deadline[1] if deadline else ""))
    return tuple(result)


def parse_page(entry: Entry, content: str, config: Config) -> Page:
    maturity = ""
    if content.startswith("---\n"):
        front, separator, _ = content[4:].partition("\n---\n")
        if not separator:
            raise ConventionError("CONFIG", f"unclosed front matter in {entry.path}")
        raw = parse_yaml(front)
        metadata = mapping(raw)
        if "maturity" in metadata:
            maturity = text(metadata["maturity"])
    blocks = parse_blocks(content, config)
    risk_titles = [block.title for block in blocks if block.fields.kind == "risk"]
    if len(risk_titles) != len(set(risk_titles)):
        raise ConventionError("R04", "risk titles must be unique within a page")
    return Page(entry, content, maturity, blocks, parse_decisions(content))


def read_pages(root: Path, entries: tuple[Entry, ...], config: Config) -> tuple[Page, ...]:
    known = {entry.path: entry for entry in entries}
    pages: list[Page] = []
    for path in sorted((root / "docs").rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        if path.is_relative_to(root / "docs/spec") or path.is_relative_to(root / "docs/generated"):
            continue
        entry = known.get(relative, Entry(path.stem, path.stem.replace("-", " "), "page", relative, "written"))
        if entry.kind == "generated":
            continue
        try:
            pages.append(parse_page(entry, path.read_text(encoding="utf-8"), config))
        except ConventionError as error:
            raise ConventionError(error.code, f"{relative}: {error.detail}") from error
    order = {entry.id: index for index, entry in enumerate(entries)}
    return tuple(sorted(pages, key=lambda page: (order.get(page.entry.id, len(order)), page.entry.path)))


def fixed_content(page: Page, config: Config) -> str:
    """Only replace managed opening and class lines; never rewrite lesson bodies."""
    lines = page.content.splitlines(keepends=True)
    thresholds = config.recent_max, config.mid_max
    for block in page.blocks:
        f = block.fields.values
        match block.fields.kind:
            case "lesson":
                title = lesson_title(f, config.as_of_year, thresholds)
                classes = ordered_classes(lesson_classes(f, config.as_of_year, thresholds))
                lines[block.start] = f"{block.fence}{{note}} {title}\n"
            case "thin":
                classes = f"hb-thin hb-thin-{f['kind']}"
            case "risk":
                classes = f"hb-risk hb-likelihood-{f['likelihood']} hb-impact-{f['impact']}"
            case _:
                assert_never(block.fields.kind)
        lines[block.start + 1] = f":class: {classes}\n"
    return "".join(lines)
