"""Gate G11: reader-scenario reachability (docs/spec/README.md, section 4).

Breadth-first search over the built HTML (``make html`` writes _build/html),
starting at index.html. One click is one internal link followed, sidebar and
table-of-contents links included. A scenario passes when its target page is
reached within ``max_clicks`` and, for an anchored target, the page carries an
element with that id.

Codes: S01 scenario schema; S02 target unreachable; S03 anchor missing;
S04 built site missing.

Usage: venv/bin/python scripts/lint/g11_scenarios.py [--root PATH] [--html DIR]
"""

from __future__ import annotations

import argparse
import functools
import posixpath
import re
import sys
from collections import deque
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from g9_anchors import load_scenarios
from hb_common import REPO_ROOT, Finding, Repo, report
from hb_ledger import split_target

SCENARIO_KEYS = ("id", "question", "target", "max_clicks")
SCENARIO_ID_RE = re.compile(r"^S[0-9]{2,}$")
EXTERNAL_RE = re.compile(r"^([a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "a":
            if values.get("name"):
                self.ids.add(str(values["name"]))
            if values.get("href"):
                self.hrefs.append(str(values["href"]))


@dataclass(frozen=True, slots=True)
class Site:
    root: Path

    @functools.lru_cache(maxsize=None)
    def parse(self, page: str) -> tuple[tuple[str, ...], frozenset[str]]:
        parser = _LinkParser()
        parser.feed((self.root / page).read_text(encoding="utf-8", errors="replace"))
        links: list[str] = []
        for href in parser.hrefs:
            target = resolve(page, href)
            if target and target != page and (self.root / target).is_file():
                links.append(target)
        return tuple(dict.fromkeys(links)), frozenset(parser.ids)

    def clicks_to(self, target: str, limit: int) -> int | None:
        """Fewest clicks from index.html to ``target``, or None beyond ``limit``."""
        seen, queue = {"index.html": 0}, deque(["index.html"])
        while queue:
            page = queue.popleft()
            depth = seen[page]
            if page == target:
                return depth
            if depth == limit:
                continue
            for link in self.parse(page)[0]:
                if link not in seen:
                    seen[link] = depth + 1
                    queue.append(link)
        return None


def resolve(current: str, href: str) -> str | None:
    """Resolve an href against the current page; None for external or same-page links."""
    if EXTERNAL_RE.match(href):
        return None
    path = href.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return None
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(current), path))
    if href.split("#", 1)[0].endswith("/"):
        joined = posixpath.join(joined, "index.html")
    return None if joined.startswith("..") else joined


def html_page(entry_path: str) -> str:
    return entry_path.removeprefix("docs/").removesuffix(".md") + ".html"


def schema_findings(repo: Repo) -> list[Finding]:
    where = repo.config["paths"]["scenarios"]
    scenarios = load_scenarios(repo)
    findings: list[Finding] = []
    if len(scenarios) < 15:
        findings.append(Finding("S01", where, 0, f"at least 15 scenarios are required; found {len(scenarios)}"))
    seen: set[str] = set()
    for number, item in enumerate(scenarios, start=1):
        if not isinstance(item, dict) or sorted(item) != sorted(SCENARIO_KEYS):
            findings.append(Finding("S01", where, 0, f"scenario {number}: keys must be exactly {', '.join(SCENARIO_KEYS)}"))
            continue
        sid = str(item["id"])
        if not SCENARIO_ID_RE.match(sid) or sid in seen:
            findings.append(Finding("S01", where, 0, f"scenario {number}: id {sid!r} is invalid or duplicated"))
        seen.add(sid)
        if not isinstance(item["question"], str) or not item["question"].strip():
            findings.append(Finding("S01", where, 0, f"{sid}: question must be non-empty text"))
        if isinstance(item["max_clicks"], bool) or item["max_clicks"] != 3:
            findings.append(Finding("S01", where, 0, f"{sid}: max_clicks must be 3"))
        if not isinstance(item["target"], str):
            findings.append(Finding("S01", where, 0, f"{sid}: target must be text"))
    return findings


def check_scenario(repo: Repo, site: Site, scenario: dict[str, Any]) -> list[Finding]:
    where = repo.config["paths"]["scenarios"]
    sid = scenario["id"]
    page_id, slug = split_target(scenario["target"])
    entry = repo.entries_by_id.get(page_id)
    if entry is None:
        return [Finding("S02", where, 0, f"{sid}: target {page_id!r} is not in the chapter list")]
    if not (site.root / "index.html").is_file():
        return [Finding("S04", where, 0, f"{sid}: no built site at {site.root}; run make html first")]
    target = html_page(entry.path)
    limit = int(scenario["max_clicks"])
    clicks = site.clicks_to(target, limit) if (site.root / target).is_file() else None
    if clicks is None:
        return [Finding("S02", where, 0, f"{sid}: {target} is not reachable from index.html within {limit} clicks")]
    if slug is not None and slug not in site.parse(target)[1]:
        return [Finding("S03", where, 0, f"{sid}: {target} has no element with id {slug!r}")]
    return []


def check(repo: Repo, html_root: Path | None = None) -> list[Finding]:
    site = Site(html_root or repo.path("_build/html"))
    findings = schema_findings(repo)
    for scenario in load_scenarios(repo):
        if isinstance(scenario, dict) and all(k in scenario for k in SCENARIO_KEYS):
            findings.extend(check_scenario(repo, site, scenario))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--html", type=Path, default=None)
    args = parser.parse_args(argv)
    return report(check(Repo(args.root), args.html), "G11 reader scenarios")


if __name__ == "__main__":
    sys.exit(main())
