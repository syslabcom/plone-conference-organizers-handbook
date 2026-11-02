# Part 5 evidence generator

Run from the repository root:

```sh
venv/bin/python scripts/evidence/build_evidence.py
venv/bin/python scripts/evidence/build_evidence.py --check
venv/bin/python -m pytest scripts/evidence/tests/
make html SPHINXOPTS="-W --keep-going"
venv/bin/python -m pytest tests/test_g5_conventions.py tests/test_g6_manifest.py
```

`--root PATH` selects an isolated repository tree for fixtures.
`--check` writes nothing, lists missing or changed pages, and exits 1 on drift.
Normal generation exits 0 and overwrites only the five owned chapter-list paths.
Input errors fail before any output is written.

## Inputs and ownership

- `data/sources/manifest.csv` supplies source IDs, groups, titles, original locations and archive paths.
- `manifest.json` supplies the three source blocks; their combined ID set must match CSV, with duplicate Seattle copies counted once.
- `archive-audit.csv` supplies license and publication recommendations.
- `data/ledger/*.yml` supplies evidence text, provenance and dispositions.
- `docs/spec/chapter-list.yml` supplies output IDs, titles, kinds and paths.
- `handbook-config.yml` supplies the pinned ranking year and age thresholds.

All inputs are read-only.
The generator does not import, invoke or change `scripts/generate` or `scripts/lint`.
It uses the repository's declared PyYAML dependency and the standard library.
Parsed YAML/JSON shapes have TypedDict boundary declarations, with immutable dataclasses used by renderers; repository gates remain responsible for the full source schemas.

| ID | Output |
|---|---|
| `conference-index` | `docs/evidence/conference-index.md` |
| `conference-data-table` | `docs/evidence/conference-data-table.md` |
| `cost-benchmarks` | `docs/evidence/cost-benchmarks.md` |
| `source-bibliography` | `docs/evidence/source-bibliography.md` |
| `lessons-ledger` | `docs/evidence/lessons-ledger.md` |

There is no separate ranking-rule entry in the chapter list.
The table explains ranking and links the existing `how-to-read-lessons` page.
The separate `lesson-index` remains owned by the convention generator.

## Publication boundaries

Explicit `exclude-pending-review` recommendations suppress file links and original URLs.
Held-back bibliography entries contain only source ID, title and reason classes.
Audit rows missing altogether fail closed into the same hold, labeled `audit row missing` and `licence unclear`.
Raw audit reasons are never copied because they can contain personal addresses.
Allowed archive copies use the stock Sphinx `download` role with relative paths under `data/sources`; Sphinx copies them into its download output.
Each source retains its own license.
The audit's historical `bibliography/` paths are not used: CSV paths identify the files in this repository.

The ledger page reproduces the separately screened ledger evidence, including dropped rows and source IDs whose archived originals are held.
It links those IDs to bibliography notices, never directly to held files.
It preserves scope, confidence, status, placement, locator and contradiction metadata.

Attendance phrases are extracted only when numbers explicitly qualify attendees, participants, registrants, sprinters or people.
Full evidence remains in L-ID footnotes, including observations without a count and incompatible populations.
No count is inferred from ticket sums, countries, talks, streams or financial figures.
Every year from 2003 through 2026 gets a row; unsupported cells contain an em dash.
The cost view includes only rows explicitly placed at `cost-benchmarks`, sorted by year and L-ID.
The ledger view sorts by L-ID; the bibliography sorts by group then source ID.
No renderer reads the clock or inserts build timestamps.

## Schema and integration tensions

- The supplied files contain 105 unique source IDs, not 93: 93 audited sources plus 12 internal-2026 additions without audit rows.
- `conference-data-table` and `cost-benchmarks` have kind `page`, so they receive full draft front matter with `review-by: 2028-11-02`.
  The other three have kind `generated`, so their front matter is minimal, as required by the generated variant.
  All five carry the C13 generated-file header immediately after front matter.
- The five chapter-list entries remain `planned` because this task forbids editing the spec.
  The integrator must mark them `written`; otherwise the strict planned-page contract tests can report unexpected passes.
- The root toctree supplied at task start has no `evidence/` entry.
  The conference index includes the other four pages in a stock toctree, but an integrator must attach that index to the root navigation.
  No `orphan` metadata or warning suppression is used.
- Bristol proportions and dated fee rows are not placed at `cost-benchmarks` in the supplied ledger.
  They are not silently reassigned by the generator.

## Tests

`tests/fixtures` contains a small repository with public, excluded and unaudited sources, duplicate Seattle JSON IDs, conflicting attendance, sprint attendance and a dropped ledger row.
The five golden documents under `tests/golden` are fixed expected artifacts.
Tests compare actual CLI output against them and exercise doctored-file rejection, regeneration recovery, input-order stability, held-file suppression, manifest ID disagreement and population labeling.
Golden files are never updated by a test run.
If rendering changes intentionally, generate against a temporary copy of the fixture tree and review changes to the fixed golden artifacts.
