"""Deterministic MyST views of the evidence archive."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from pathlib import Path
from urllib.parse import quote

from .models import Evidence, Lesson, Page


def text(value: str) -> str:
    """Escape input prose for Markdown table cells and inline labels."""
    return (" ".join(value.split()).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace("|", "&#124;").replace("[", "\\[")
            .replace("]", "\\]").replace("`", "\\`"))


def relative(origin: Page, target: str) -> str:
    return quote(os.path.relpath(target, Path(origin.path).parent), safe="/#")


def header(page: Page) -> str:
    """Respect the chapter-list kind even when the body is machine-written."""
    ownership = ""
    # G4 C01/C13: only kind "generated" may carry the marker above the H1; other kinds carry it below.
    marker = "<!-- generated: do not edit; run the generator -->\n\n"
    trailer = ""
    if page.kind != "generated":
        marker, trailer = "", marker
        ownership = ("steward: unassigned\ndeputy: unassigned\nreview-by: 2028-11-02\n"
                     "maturity: draft\napplies-to: [all]\n")
    return (f"---\n{ownership}diataxis: reference\nmyst:\n  html_meta:\n"
            f'    "description lang=en": "Evidence for Plone conference organizers: {page.title.lower()}, with traceable sources."\n'
            '    "keywords": "Plone, Plone Conference, evidence, archive"\n---\n'
            f"{marker}# {page.title}\n\n{trailer}")


def source_link(row: Lesson) -> str:
    return f"[{row.source_id}](#{row.source_id.lower()})"


def bibliography(evidence: Evidence) -> str:
    page = evidence.page("source-bibliography")
    lines = [header(page), "Archive recommendations control access to copies below.\n",
             "An archived copy retains its source license; inclusion does not relicense third-party material.\n"]
    groups = sorted({source.group for source in evidence.sources})
    for group in groups:
        lines.extend([f"\n(bibliography-{group})=\n", f"## {group.replace('-', ' ')}\n"])
        for source in (item for item in evidence.sources if item.group == group and not item.held):
            lines.extend([f"\n({source.id.lower()})=\n", f"### {source.id}: {text(source.title)}\n",
                          f"\n{{download}}`Archived copy <{relative(page, 'data/sources/' + source.file)}>`\n"])
            if source.url.startswith(("https://", "http://")):
                lines.append(f"\nOriginal URL: <{source.url}>\n")
            else:
                lines.append(f"\nOriginal repository location: `{source.url}` (no public original URL).\n")
            lines.append(f"\nLicense: `{source.licence}`. Recommendation: `{source.recommendation}`.\n")
            if source.archive_note:
                lines.append(f"\nArchive note: {text(source.archive_note)}.\n")
        held = [source for source in evidence.sources if source.group == group and source.held]
        if held:
            lines.append("\n### Held back pending review\n\nNo archive files or original locations are linked in this subsection.\n")
            for source in held:
                lines.append(f"\n({source.id.lower()})=\n\n- {source.id}: {text(source.title)}. Reason class: {source.reason or 'licence unclear'}; recommendation: `exclude-pending-review`.\n")
    return "".join(lines)


def footnotes(rows: tuple[Lesson, ...]) -> str:
    return "\n" + "\n\n".join(
        f"[^{row.ledger_id}]: {row.ledger_id}, as of {row.year}, {source_link(row)}, " +
        f"{row.confidence}, {row.status}. {text(row.quote_or_paraphrase)}"
        for row in rows
    ) + "\n"


def cells(rows: tuple[Lesson, ...], field: Callable[[Lesson], str]) -> str:
    """Keep conflicting observations separate; never silently choose a winner."""
    values: list[str] = []
    for row in rows:
        value = field(row)
        if value and value != "n/a":
            values.append(f"{text(value)}[^{row.ledger_id}]")
    return "<br>".join(values) or "—"


def conference_table(evidence: Evidence) -> str:
    page = evidence.page("conference-data-table")
    rows = evidence.placed(page.id)
    method = relative(page, evidence.page("how-to-read-lessons").path)
    lines = [header(page), "## Reading the evidence\n\n",
             "These are specific, dated observations, not general recommendations.\n",
             "General lessons require three independent conferences across two organizing bodies, or a structural reason independent of year.\n",
             f"See [How to read lessons]({method}) for promotion and ranking.\n",
             f"The pinned reference year is {evidence.as_of}; ages 0–{evidence.recent} are recent, " +
             f"{evidence.recent + 1}–{evidence.mid} are mid, and older evidence is stale-prone.\n",
             "General lessons rank first; specific lessons sort by year descending, confidence (observed, reported, hearsay), then first ledger ID.\n",
             "Conflicting counts and populations remain separate; stream viewers, sprinters and registrants are not interchangeable.\n",
             "A dash means no matching ledger evidence; it does not mean zero attendance.\n\n",
             "## Conference observations\n\n",
             "| Year | Attendance where stated | Place | Organizer | Co-location notes |\n",
             "|---|---|---|---|---|\n"]
    for year in range(2003, 2027):
        selected = tuple(row for row in rows if row.year == year)
        attendance: list[str] = []
        notes: list[str] = []
        for row in selected:
            matches = re.findall(
                r"(?:more than |around |about |over |roughly )?[\d,]+(?: on-site)? " +
                r"(?:attendees|participants|registrants|sprinters|people)(?: in person)?",
                row.quote_or_paraphrase, re.IGNORECASE,
            )
            if matches:
                attendance.append(f"{'; '.join(matches)}[^{row.ledger_id}]")
            if re.search(r"together|joint|co-locat", row.quote_or_paraphrase, re.IGNORECASE):
                notes.append(f"{text(row.quote_or_paraphrase)}[^{row.ledger_id}]")
        year_refs = "".join(f"[^{row.ledger_id}]" for row in selected)
        lines.append(f"| {year}{year_refs} | {'<br>'.join(attendance) or '—'} | " +
                     f"{cells(selected, lambda row: row.place)} | {cells(selected, lambda row: row.org)} | {'<br>'.join(notes) or '—'} |\n")
    lines.append("\n## Evidence notes\n\nAll placed rows are preserved below, including contextual observations without an attendance count.\n")
    lines.append(footnotes(rows))
    return "".join(lines)


def costs(evidence: Evidence) -> str:
    page = evidence.page("cost-benchmarks")
    lines = [header(page), "```{warning} Dated snapshots\n",
             "These public figures describe their stated year, currency, scope and location.\n",
             "They are not quotes for a future conference or inflation-adjusted comparisons.\n",
             "Obtain dated local quotes and check taxes, inclusions and exchange rates before budgeting.\n```\n\n",
             "Only rows placed at this page are listed; no amounts are inferred from other ledger topics.\n\n",
             "| As-of year | Place | Sourced cost observation | Evidence |\n|---|---|---|---|\n"]
    for row in sorted(evidence.placed(page.id), key=lambda item: (item.year, item.ledger_id)):
        lines.append(f"| {row.year} | {text(row.place)} | {text(row.quote_or_paraphrase)} | " +
                     f"[{row.ledger_id}](#{row.ledger_id.lower()}), {source_link(row)} |\n")
    return "".join(lines)


def conference_index(evidence: Evidence) -> str:
    page = evidence.page("conference-index")
    lines = [header(page), "Each year links to its bibliography group where sources exist.\n",
             "A missing case file or bibliography group records an evidence gap.\n\n"]
    groups = sorted({source.group for source in evidence.sources})
    for year in range(2003, 2027):
        links = [f"[{group.replace('-', ' ')}](#bibliography-{group})"
                 for group in groups if group.startswith(str(year))]
        records = sorted(path for path in (evidence.root / "docs/conferences").glob(f"{year}-*/*.md")
                         if path.name != "README.md")
        links.extend(f"[Case file]({relative(page, path.relative_to(evidence.root).as_posix())})" for path in records)
        if not links:
            links.append("[General conference history](#bibliography-general-and-current-planning-resources); no year-specific group or case file")
        lines.append(f"- {year}: {'; '.join(links)}.\n")
    lines.append("\n## Evidence pages\n\n```{toctree}\n:maxdepth: 1\n\nconference-data-table\ncost-benchmarks\nsource-bibliography\nlessons-ledger\n```\n")
    return "".join(lines)


def ledger(evidence: Evidence) -> str:
    lines = [header(evidence.page("lessons-ledger")),
             "Rows are sorted by ledger ID, including dropped and superseded evidence.\n",
             "Scope records the source claim; it does not certify promotion to a general lesson.\n",
             "The disposition records editorial placement, not publication approval of an archived original.\n",
             "Source links resolve to bibliography metadata, including held-back notices.\n"]
    for row in evidence.lessons:
        lines.extend([f"\n({row.ledger_id.lower()})=\n\n## {row.ledger_id}\n\n",
                      f"{row.year}; {text(row.place)}; {text(row.org)}; {source_link(row)}.\n",
                      f"\nScope: `{row.scope}`. Confidence: `{row.confidence}`. Status: `{row.status}`.\n",
                      f"\nTopic: `{row.topic}`. Disposition: `{row.disposition}`.\n",
                      f"\n{text(row.quote_or_paraphrase)}\n"])
        if row.locator:
            lines.append(f"\nLocator: {text(row.locator)}.\n")
        if row.issue or row.by:
            lines.append(f"\nIssue: {text(row.issue) or '—'}. Replaced by: {text(row.by) or '—'}.\n")
    return "".join(lines)
