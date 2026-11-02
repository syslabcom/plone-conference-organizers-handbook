# Lint gates (task T5)

These scripts implement the content gates of the handbook spec (`docs/spec/`).
They read the repository-root `handbook-config.yml`, use only the standard library and PyYAML, and run with the repository venv.

```shell
venv/bin/pip install -r requirements-test.txt
venv/bin/python -m pytest                 # all gates: fixture proofs and the repository's own content
venv/bin/python -m pytest -m "not repo"   # fixture proofs only
venv/bin/python scripts/lint/g5_conventions.py   # one gate from the command line
```

Every gate script takes `--root PATH` (default: this repository), prints one line per finding as `path:line: CODE message`, and exits 1 when it finds anything.

## Modules

| Module | Gate | Spec | Codes |
|---|---|---|---|
| `g3_temporal.py` | G3 temporal-word lint | chapter-template.md 7, rule 4 | W01 |
| `g4_contract.py` | G4 chapter contract | chapter-template.md 1, 6, 8; front-matter.md 4 | CL01, C00-C14, F01-F09, plus N01, R03, T02 |
| `g5_conventions.py` | G5 convention validation | conventions.md 9 | B01-B06, L01-L10, T01-T02, R01-R04, N01-N04 |
| `g6_manifest.py` | G6 manifest integrity | ledger-schema.md LD06 | M01-M05 |
| `g7_ledger.py` | G7 ledger coverage | ledger-schema.md 5, 6 | LD01-LD11 |
| `g8_privacy.py` | G8 privacy lint | ledger-schema.md 3; D7 | P01-P04 |
| `g9_anchors.py` | G9 anchor check | chapter-template.md 2 | A01-A04 |
| `g10_freshness.py` | G10 freshness report | front-matter.md 2.3, 5 | report, no codes |
| `g11_scenarios.py` | G11 reader scenarios | README.md 4 | S01-S04 |
| `convert_register.py` | requirements register converter | README.md 3 (R-IDs) | not a gate |
| `hb_common.py` | repository model, vocabularies, `Finding` | | |
| `hb_markdown.py` | fence-aware MyST parsing, managed blocks | conventions.md 2 | |
| `hb_frontmatter.py` | rules F01-F09 | front-matter.md | |
| `hb_badges.py` | rules N01-N04 (part of G5) | conventions.md 1 | |
| `hb_ledger.py` | dispositions and anchor resolution | ledger-schema.md 5 | |

G4 codes: CL01 chapter-list schema; C00 file missing; C01 H1; C02 chapter headings; C03 "Applies when" bullets; C05 source IDs; C06 word budget; C07 maturity minimums; C10 page headings; C11 playbook structure; C12 annex disclaimer; C13 generated header; C14 template files referenced.

## How the tests prove each gate

`tests/fixtures/base/` is the fixed tree: a small handbook (one chapter, one playbook, one page, one annex, a ledger, a manifest with real files and hashes, a register, 15 scenarios) in which every gate passes.
`tests/fixtures/<gate>/broken/<case>/` overlays change one thing in the base.
The case name starts with the rule code it must trigger, and the test asserts that the gate reports exactly that set of codes, so a broken case cannot pass by failing for a different reason.
`tests/fixtures/<gate>/fixed/` adds what a gate needs beyond the base (an allowlist, a built HTML site, dated temporal words).

Tests that take the `real_repo` fixture carry the `repo` marker and judge this repository's own content.
G4 runs one test per chapter-list entry and G11 one test per scenario; both are `xfail(strict=True)` while the target entry has `status: planned`, so a page that passes while still planned fails the suite.
`test_xfail_strict_turns_an_unexpected_pass_into_a_failure` proves this by running pytest on a fixture tree.

## Interfaces for other tasks

- **T8, scheduled freshness workflow.** Run `venv/bin/python scripts/lint/g10_freshness.py --format json`.
  It prints a JSON list of `{id, title, path, review_by, steward, deputy}` for written pages past `review-by`.
  `--as-of YYYY-MM-DD` overrides today; `--fail-on-overdue` exits 1 when the list is not empty.
  Pull-request CI runs it report-only.
- **T4, requirements register.** `venv/bin/python scripts/lint/convert_register.py` regenerates `data/requirements-register.yml` from the Markdown register in the sibling `ploneconference` checkout (`--input` overrides the path, `--check` reports drift).
- **T6, generator.** The pure functions `lesson_title` and `lesson_classes` in `g5_conventions.py` follow conventions.md 3.3 with the config thresholds; reuse them rather than reimplementing.
- **G8 allowlist.** `scripts/lint/privacy-allowlist.yml`. Each entry needs `match` (the exact hit), `reason`, and optionally `paths` (globs).

## Readings where the spec was ambiguous (the stricter reading was chosen)

1. **Lint as-of date (F04, G10).** The spec does not define "the lint's as-of date". It is today, overridable with `--as-of`. Ages of lessons still use the pinned `as-of-year`.
2. **H1 placement (C01).** The H1 is the first heading and the first content after the front matter (MyST target labels and `%` comments excepted). On generated pages the generated header comment comes first.
3. **Chapter intro text (C02).** Nothing may stand between a chapter's H1 and its first H2, because section 2 lists the H1 and the nine H2s as the whole page.
4. **Applies-to dimensions (F06).** A dimension may appear in only one `applies-to` item.
5. **Decision grammar (N01).** Besides exactly one badge, each section 3 decision needs a bold question ending in `?`, and a `decide-by` must match `(decide-by: T-<n><d|w|m>)`. A badge in a nested sub-bullet counts against its decision. Section 3 must hold at least one top-level item.
6. **Badge grammar codes.** A malformed MUST badge reports N02, a malformed DEFAULT N03, an OPTION with a parenthesis or the wrong color N01. Badges inside managed blocks report N04; badges inside other fences (code examples) are text and ignored.
7. **DEFAULT evidence (N03).** A DEFAULT may not cite a `hearsay` row (ledger-schema.md 4) or a dropped row.
8. **Description sentence (F08).** The description must end with a period, besides the length and temporal-word rules.
9. **Stub thin markers (T02).** "A stub holds at least one thin block" applies to every kind that may hold thin blocks: chapter, page, annex and appendix. Playbooks and generated pages are exempt.
10. **Thin blocks in playbooks (B05).** The placement table lists only page, annex and appendix for thin blocks outside chapters, so a thin block in a playbook fails.
11. **Exact section sentences (T02, R03).** Without a block, the section must contain exactly the one sentence and nothing else.
12. **Block titles.** Thin and risk titles that break the 1-80 character, no-backtick rule report B03.
13. **Source IDs in code examples.** Source IDs inside non-admonition fences (for example a Markdown example) are not citations, for C05 and M04 alike. Prose and admonition bodies count.
14. **Temporal words (W01).** A dated anchor is `YYYY-MM` or `YYYY-MM-DD` on the same source line (one sentence per line). A bare year is not enough. Admonition titles and bodies are prose; code fences, inline code, URLs and link targets are not. `docs/spec/` is excluded, like in Vale.
15. **Privacy scope (G8).** The whole tree is scanned. Excluded explicitly: `data/sources/` (pre-publication archive, audited by T3), `tests/fixtures/` (deliberate violations), and tool directories (`.git`, `venv`, `.venv`, `_build`, `node_modules`, `styles/Microsoft`, caches). IBAN candidates count only when the ISO 13616 checksum is valid; phone candidates need 8-15 digits.
16. **Manifest file paths (G6).** The `file` column is relative to the manifest's directory and must stay inside it.
17. **Cited sources (G6).** Ledger rows, lesson `source` fields, prose source IDs on every published page, and the register's `source-ids` all count.
18. **Bibliography coverage (G6, M05).** Until T10 generates it, G6 checks that a generated `source-bibliography` entry exists. Once that page is written, every manifest ID must appear in it.
19. **Ledger consistency (G7, LD10).** G7 checks both directions of ledger-schema.md 5.3 (row to page and page to row), so it overlaps with G5 rule L10 on purpose.
20. **Anchors on the T-minus checklist (G9).** The spec does not fix their syntax. G9 checks `` `<id>#<slug>` `` tokens in inline code on that page, with the disposition rules.
21. **Scenario anchors (G9).** An anchor on a page, annex, appendix or generated target is invalid (A03), because only chapters and playbooks have slug sets.
22. **G11 links.** Any internal `<a href>` in the built HTML is a click (sidebar and table of contents included); same-page links are not.
23. **Register conversion.** An em dash (no value) becomes null. Source IDs are resolved from `BIB/` paths and live URLs against the manifest; "CFP set as in R04" expands to the four archived CFPs plus the live 2020 CFP, as the register's footnote defines. Unresolved references are kept in `unresolved-sources`.

## Not checked by a script

Sentence-case headings, one sentence per line, the 80-word lesson body limit, plain-language rules, and the per-group source coverage of the ledger (the spec gives no machine-readable group-to-source mapping).
Reviewers check these by reading.

## Typing

The modules are fully annotated and compile on Python 3.11 and later.
Under basedpyright's `all` mode the remaining reports are of three kinds, all deliberate: `Any` from parsed YAML and CSV at the boundary, implicit relative imports (the scripts are a flat directory run as `venv/bin/python scripts/lint/<gate>.py`, not a package), and unused `argparse` return values.
`pyrightconfig.json` does not include `scripts/lint`.
