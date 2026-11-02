"""Gate G8: privacy lint (ledger-schema.md, section 3; chapter-template.md, section 7; D7).

Scans every text file of the tree for email addresses, phone numbers and
IBANs. Any hit fails unless the allowlist (scripts/lint/privacy-allowlist.yml)
names it with a reason.

Excluded on purpose, and only these:
- data/sources/: the pre-publication source archive, audited separately (T3).
- tests/fixtures/: deliberate violations that prove the gates fail.
- tool and build directories: .git, venv, .venv, _build, node_modules,
  styles/Microsoft (the synced third-party Vale package), caches.

Codes: P01 email, P02 phone number, P03 IBAN, P04 allowlist invalid.

Usage: venv/bin/python scripts/lint/g8_privacy.py [--root PATH] [FILE ...]
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from hb_common import REPO_ROOT, Finding, Repo, rel, report

ALLOWLIST = "scripts/lint/privacy-allowlist.yml"
EXCLUDED_DIRS = (
    ".git", "venv", ".venv", "_build", "node_modules", "__pycache__", ".pytest_cache",
    "data/sources", "tests/fixtures", "styles/Microsoft",
)
TEXT_SUFFIXES = frozenset(
    {".md", ".rst", ".txt", ".yml", ".yaml", ".csv", ".json", ".py", ".toml", ".cfg", ".ini", ".html", ".css", ".js", ""}
)
EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?![A-Za-z0-9-])")
PHONE_RES = (
    # International: a plus sign or 00, a country code, then digit groups.
    re.compile(r"(?<![\w+])(?:\+|00)[1-9][0-9]{0,2}[ .\-/]?(?:\(?[0-9]{1,5}\)?[ .\-/]?){1,4}[0-9]{2,}(?![\w-])"),
    # North American: a three-digit area code, three digits, a hyphen, four digits.
    re.compile(r"(?<![\w-])\(?[2-9][0-9]{2}\)?[ .-][0-9]{3}-[0-9]{4}(?![\w-])"),
    # European national: a trunk zero and area code, a separator, then digit groups.
    re.compile(r"(?<![\w.,-])0[1-9][0-9]{1,4}[ /-][0-9]{2,8}(?:[ -][0-9]{2,4}){0,3}(?![\w-]|[.,][0-9])"),
)
IBAN_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}[0-9]{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,3})?(?![A-Za-z0-9])")


@dataclass(frozen=True, slots=True)
class Allow:
    match: str
    paths: tuple[str, ...]


def iban_valid(candidate: str) -> bool:
    """ISO 13616 mod-97 check, so only real-shaped IBANs count."""
    compact = candidate.replace(" ", "")
    if not 15 <= len(compact) <= 34:
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(int(ch, 36)) for ch in rearranged)
    return int(digits) % 97 == 1


def phone_like(candidate: str) -> bool:
    digits = re.sub(r"[^0-9]", "", candidate)
    if not 8 <= len(digits) <= 15:
        return False
    # ISO dates and year ranges are not phone numbers.
    return not re.fullmatch(r"[0-9]{4}-[0-9]{2}(-[0-9]{2})?", candidate.strip())


def load_allowlist(repo: Repo) -> tuple[list[Allow], list[Finding]]:
    path = repo.path(ALLOWLIST)
    if not path.is_file():
        return [], []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries: list[Allow] = []
    findings: list[Finding] = []
    for number, item in enumerate(data.get("allow", []) if isinstance(data, dict) else [], start=1):
        if not (isinstance(item, dict) and isinstance(item.get("match"), str) and isinstance(item.get("reason"), str) and item["reason"].strip()):
            findings.append(Finding("P04", ALLOWLIST, number, "each allowlist entry needs 'match' and a non-empty 'reason'"))
            continue
        paths = item.get("paths") or ["**"]
        entries.append(Allow(item["match"], tuple(str(p) for p in paths)))
    return entries, findings


def allowed(allowlist: list[Allow], hit: str, path: str) -> bool:
    return any(a.match == hit and any(fnmatch.fnmatch(path, p) for p in a.paths) for a in allowlist)


def scan_files(repo: Repo) -> list[Path]:
    root = repo.root.resolve()
    excluded = [root / d for d in EXCLUDED_DIRS]
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(ex == path or ex in path.parents for ex in excluded):
            continue
        files.append(path)
    return files


def scan_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line, code, hit) for every privacy pattern hit in a text."""
    hits: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in EMAIL_RE.finditer(line):
            hits.append((number, "P01", match.group(0)))
        masked = EMAIL_RE.sub(" ", line)
        for match in IBAN_RE.finditer(masked):
            if iban_valid(match.group(0)):
                hits.append((number, "P03", match.group(0)))
        masked = IBAN_RE.sub(" ", masked)
        for pattern in PHONE_RES:
            for match in pattern.finditer(masked):
                if phone_like(match.group(0)):
                    hits.append((number, "P02", match.group(0).strip()))
            masked = pattern.sub(" ", masked)
    return hits


def check_paths(repo: Repo, paths: list[Path]) -> list[Finding]:
    allowlist, findings = load_allowlist(repo)
    for path in paths:
        if path.resolve() == repo.path(ALLOWLIST).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        where = rel(repo, path)
        for line, code, hit in scan_text(text):
            if not allowed(allowlist, hit, where):
                kind = {"P01": "email address", "P02": "phone number", "P03": "IBAN"}[code]
                findings.append(Finding(code, where, line, f"{kind} {hit!r} (D7: no contact details; allowlist it with a reason if it is a public role address)"))
    return findings


def check(repo: Repo, files: list[Path] | None = None) -> list[Finding]:
    return check_paths(repo, files if files is not None else scan_files(repo))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    repo = Repo(args.root)
    return report(check(repo, [p.resolve() for p in args.files] or None), "G8 privacy")


if __name__ == "__main__":
    sys.exit(main())
