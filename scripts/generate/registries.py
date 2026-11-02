"""Deterministic Markdown rendering for the five convention registries."""

import html
from collections.abc import Iterable
from pathlib import PurePosixPath
from typing import Final

from .fields import AREAS
from .lessons import lesson_title
from .models import Block, Config, Entry, Page
from .render import slug

GENERATED: Final = ("lesson-index", "risk-register", "thin-registry", "decision-register", "coverage-map")
THIN_KINDS: Final = ("gap", "single-source", "stale")
CONFIDENCE: Final = {"observed": 0, "reported": 1, "hearsay": 2}
SCORES: Final = {"low": 1, "medium": 2, "high": 3}


def cell(value: str) -> str:
    return html.escape(value, quote=False).replace("|", "&#124;").replace("\n", " ").replace("[", "\\[").replace("]", "\\]")


def table(headers: tuple[str, ...], rows: Iterable[Iterable[str]]) -> str:
    rendered = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    rendered.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(rendered) + "\n\n"


def page_link(entry: Entry, anchor: str = "", label: str = "") -> str:
    target = PurePosixPath(entry.path).relative_to("docs").as_posix()
    if entry.kind == "generated" and entry.id in GENERATED:
        target = f"generated/{entry.id}.md"
    return f"[{cell(label or entry.title)}](../{target}{'#' + anchor if anchor else ''})"


def lesson_key(block: Block) -> tuple[int, int, int, str]:
    f = block.fields.values
    if f["scope"] == "general":
        return (0, 0, 0, f["ledger"].split(",")[0].strip())
    return (0 if f["scope"] == "general" else 1, -int(f.get("year", "0")), CONFIDENCE[f["confidence"]], f["ledger"].split(",")[0].strip())


def lesson_index(pages: tuple[Page, ...], config: Config) -> str:
    output = ""
    for page in pages:
        blocks = sorted((block for block in page.blocks if block.fields.kind == "lesson"), key=lesson_key)
        if not blocks:
            continue
        output += f"## {page_link(page.entry)}\n\n"
        rows: list[list[str]] = []
        for block in blocks:
            f = block.fields.values
            rows.append([cell(lesson_title(f, config.as_of_year, (config.recent_max, config.mid_max))), *(cell(f[key]) for key in ("scope", "confidence", "status", "ledger", "source"))])
        output += table(("Title", "Scope", "Confidence", "Status", "Ledger", "Sources"), rows)
    return output or "No lessons recorded.\n"


def risk_score(block: Block) -> int:
    f = block.fields.values
    return SCORES[f["likelihood"]] * SCORES[f["impact"]]


def risk_id(page: Page, block: Block) -> str:
    return f"{page.entry.id}#risk-{slug(block.title)}"


def risk_register(pages: tuple[Page, ...], entries: tuple[Entry, ...]) -> str:
    playbooks = {entry.id: entry for entry in entries if entry.kind == "playbook"}
    indexed = [(index, page, block) for index, page in enumerate(pages) for block in page.blocks if block.fields.kind == "risk"]
    indexed.sort(key=lambda row: (-risk_score(row[2]), row[0], row[2].title))
    rows: list[list[str]] = []
    for _, page, block in indexed:
        f = block.fields.values
        playbook = f.get("playbook", "")
        if playbook and playbook not in playbooks:
            from .models import ConventionError
            raise ConventionError("R02", f"unknown playbook: {playbook}")
        linked = page_link(playbooks[playbook]) if playbook else ""
        risk_link = f"{{ref}}`{cell(block.title)} <{risk_id(page, block)}>`"
        rows.append([risk_link, page_link(page.entry), cell(f["likelihood"]), cell(f["impact"]), str(risk_score(block)), cell(f["mitigation"]), cell(f.get("owner-role", "")), linked])
    return table(("Risk", "Page", "Likelihood", "Impact", "Score", "Mitigation", "Owner role", "Playbook"), rows)


def thin_registry(pages: tuple[Page, ...]) -> str:
    output = ""
    for kind in THIN_KINDS:
        rows: list[list[str]] = []
        for page in pages:
            for index, block in enumerate(page.blocks):
                f = block.fields.values
                if block.fields.kind != "thin" or f["kind"] != kind:
                    continue
                issue = f.get("issue", "")
                if issue.startswith("https://"):
                    issue = f"[{cell(issue)}]({issue})"
                else:
                    issue = cell(issue)
                thin_link = f"{{ref}}`{cell(block.title)} <{page.entry.id}#thin-{index + 1}-{slug(block.title)}>`"
                rows.append([thin_link, page_link(page.entry), kind, cell(f.get("area", "")), cell(f["needs"]), cell(f["who-might-know"]), issue, cell(f.get("since", ""))])
        output += f"## {kind.capitalize()}\n\n"
        output += table(("Title", "Page", "Kind", "Area", "Needs", "Who might know", "Issue", "Since"), rows)
    return output


def decision_register(pages: tuple[Page, ...]) -> str:
    return table(("Page", "Level", "Decision", "Decide by"), (
        [page_link(page.entry), decision.level, cell(decision.question), cell(decision.decide_by)]
        for page in pages for decision in page.decisions
    ))


def coverage_map(pages: tuple[Page, ...], entries: tuple[Entry, ...]) -> str:
    by_id = {page.entry.id: page for page in pages}
    rows: list[list[str]] = []
    for entry in entries:
        if entry.kind == "generated":
            continue
        page = by_id.get(entry.id)
        blocks = page.blocks if page else ()
        thin = [block.fields.values["kind"] for block in blocks if block.fields.kind == "thin"]
        lessons = [block.fields.values["scope"] for block in blocks if block.fields.kind == "lesson"]
        rows.append([cell(entry.id), cell(entry.status), cell(page.maturity if page else ""), *(str(thin.count(kind)) for kind in THIN_KINDS), str(lessons.count("general")), str(lessons.count("specific")), str(sum(block.fields.kind == "risk" for block in blocks))])
    output = table(("id", "Status", "Maturity", "Thin: gap", "Thin: single-source", "Thin: stale", "Lessons: general", "Lessons: specific", "Risk blocks"), rows)
    areas = [block.fields.values.get("area") for page in pages for block in page.blocks if block.fields.kind == "thin"]
    output += "## Predicted thin areas\n\n" + table(("Area", "Thin markers"), ([area, str(areas.count(area))] for area in AREAS))
    return output


def generated_pages(pages: tuple[Page, ...], entries: tuple[Entry, ...], config: Config) -> dict[str, str]:
    bodies = {
        "lesson-index": lesson_index(pages, config),
        "risk-register": risk_register(pages, entries),
        "thin-registry": thin_registry(pages),
        "decision-register": decision_register(pages),
        "coverage-map": coverage_map(pages, entries),
    }
    result: dict[str, str] = {}
    for name, body in bodies.items():
        title = name.replace("-", " ").capitalize()
        description = f"{title} for the Plone Conference Organizers Handbook, generated from the handbook conventions."
        result[f"docs/generated/{name}.md"] = (
            "---\ndiataxis: reference\nmyst:\n  html_meta:\n"
            f'    "description lang=en": "{description}"\n'
            f'    "keywords": "Plone, conference, {title.lower()}"\n'
            "---\n<!-- generated: do not edit; run the generator -->\n\n"
            f"# {title}\n\n{body}"
        )
    return result
