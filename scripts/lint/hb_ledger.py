"""Anchor and disposition helpers shared by G5, G7 and G9 (ledger-schema.md, section 5)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from hb_common import Repo, slugs_for_kind

PLACED_RE = re.compile(r"^placed: ([a-z][a-z0-9-]*)(?:#([a-z][a-z0-9-]*))?$")
DROPPED_RE = re.compile(r"^dropped: (.{15,})$")
PLACEHOLDERS = frozenset({"n/a", "na", "tbd", "todo", "none", "-", "?", "xxx", "fixme"})


@dataclass(frozen=True, slots=True)
class Placement:
    page: str
    slug: str | None


def parse_disposition(value: object) -> tuple[Placement | None, str | None]:
    """Return (placement for placed rows, error). Dropped rows return (None, None)."""
    if not isinstance(value, str) or not value.strip():
        return None, "disposition is missing or empty"
    if match := PLACED_RE.match(value):
        return Placement(match.group(1), match.group(2)), None
    if match := DROPPED_RE.match(value):
        reason = match.group(1).strip()
        if reason.lower().rstrip(".") in PLACEHOLDERS or len(reason) < 15:
            return None, f"dropped reason {reason!r} is a placeholder"
        return None, None
    if value.startswith("dropped:"):
        return None, "dropped reason must be a sentence of at least 15 characters"
    return None, f"disposition {value!r} is neither 'placed: <page>[#slug]' nor 'dropped: <reason>'"


def anchor_error(repo: Repo, page: str, slug: str | None, *, purpose: str) -> tuple[str, str] | None:
    """Validate ``page#slug`` against the chapter list and the slug sets.

    ``purpose`` is ``disposition`` (ledger rule 5.1: chapters and playbooks need a slug,
    other kinds must not have one, generated pages are not targets) or ``scenario``
    (README section 4: the anchor is optional, valid only on chapters and playbooks).
    Returns (code, message) or None.
    """
    entry = repo.entries_by_id.get(page)
    if entry is None:
        return "A01", f"{page!r} is not a chapter-list id"
    if purpose == "disposition" and entry.kind == "generated":
        return "A04", f"{page!r} is a generated page and cannot be a target"
    valid = slugs_for_kind(entry.kind)
    if slug is None:
        if purpose == "disposition" and valid:
            return "A03", f"{page!r} has kind {entry.kind}; the target needs '#<section slug>'"
        return None
    if not valid:
        return "A03", f"{page!r} has kind {entry.kind}; it takes no anchor (found #{slug})"
    if slug not in valid:
        return "A02", f"#{slug} is not a valid {entry.kind} slug for {page!r}"
    return None


def split_target(target: str) -> tuple[str, str | None]:
    page, sep, slug = target.partition("#")
    return page, (slug if sep else None)
