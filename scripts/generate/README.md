# Convention generator

Independent implementation of the frozen stock-admonition specification.
No imports from `scripts/lint/` or `tests/`; T5 can cross-check the public functions against its own implementation.
Runtime dependency: PyYAML, supplied by the repository virtual environment.

## Commands

Run from the repository root:

```sh
venv/bin/python -m scripts.generate generate
venv/bin/python -m scripts.generate fix docs/path/to/chapter.md
venv/bin/python -m scripts.generate fix
venv/bin/python -m scripts.generate check
venv/bin/python -m pytest scripts/generate/tests -v
make html SPHINXOPTS="-W --keep-going"
```

`generate` writes the five registries, without changing authored pages.
`fix` repairs computed titles and classes, either in the named pages or across the whole documentation tree, and regenerates the registries.
It preserves field lines, lesson bodies and author-written warning titles.
`check` computes both repairs and registries without writing anything.
Exit codes: 0 for clean/success, 1 for drift, 2 for invalid input or invocation.
`--root DIR` selects another repository, including isolated test fixtures.
No mode reads the clock or writes timestamps.

## Layout and public API

- `models.py`: immutable configuration, page and block records; YAML input boundary.
- `fields.py`: independent physical-line parser and field validation.
- `lessons.py`: `age_bucket`, `lesson_title`, `lesson_classes`, stable class serialization.
- `documents.py`: top-level fence scanner, block and decision extraction, computed-line repair.
- `registries.py`: stable Markdown tables and generated-page front matter.
- `render.py`: build-time translation to stock admonitions and closed dropdowns, including block link targets.
- `__main__.py`: CLI, filesystem writes and drift exit codes.
- `fixtures/`: synthetic chapter and invalid field-line cases.
- `tests/`: parser, age, registry and real-CLI regression tests.

`parse_field_line(line, config=Config(), implied_kind=None)` returns `Fields(kind, values)`.
It enforces field syntax, required/forbidden fields, local value vocabularies and conditional status fields.
Failures carry a `ConventionError.code` from the spec's catalog.
`lesson_title(fields.values, as_of_year, thresholds=(3, 8))` and `lesson_classes(...)` implement section 3.3.
The optional third argument supplies configured thresholds; the two-argument form matches the spec's defaults.
Cross-file evidence validity, promotions, contradictions, chapter placement and normative evidence remain T5 lint responsibilities.
The generator does not infer or promote claims from ledger rows.

## Output and spec reconciliation

The task explicitly requires `docs/generated/`, while the frozen chapter list names other directories for the same IDs.
This generator uses `docs/generated/{id}.md` for its five output IDs and retains the frozen chapter list for chapter ordering and coverage.
It does not change the spec, create duplicate pages at the old locations, or mark planned entries as written.
When the master list is revised, its five generated paths should be aligned with these outputs.

The thin registry groups rows into gap, single-source and stale tables as requested by T6.
Within each group, page and document order follow section 8.3.
The column schema is unchanged; this is the explicit grouped presentation of the specification's single-table view.
Risk and decision registers follow master-list page order, rather than alphabetic filenames.
General lessons sort by first ledger ID; specific lessons sort by descending year, confidence, then first ledger ID.
Descending year also orders the age buckets because all lessons share the same pinned year and thresholds.

The five generated pages have only `diataxis` and `myst` front matter, followed by the required generated-file comment.
The root landing page's stock toctree includes all five.
Separate stock toctrees include the existing Start here and Running the handbook pages without changing authored content.
No `orphan` key, exclusion or warning suppression is needed, so the pages remain built and discoverable in accordance with front-matter section 1.
Risk and thin rows link to block targets added in memory by the source adapter; the generator never inserts anchors into authored content.
Missing planned chapters appear as unlinked coverage rows to avoid false Sphinx references.

## Styling choice

`docs/_static/hb.css` is loaded through `html_css_files` in `docs/conf.py`.
General lessons have the strongest border and heading weight; mid and old lessons use progressively lighter headings and distinct border patterns.
Text labels carry age and status independently of color.
MyST 5.1 warns when a `{note}` or `{warning}` has both a first-line argument and body content with options.
It also renders that argument in the body under a generic heading.
The source-read adapter registered by `docs/conf.py` translates managed blocks in memory into the stock `{admonition}` directive with their computed heading.
Old specific lessons instead render through the stock `sphinx_design` `{dropdown}` directive, closed by default.
The required authored `{note}` and `{warning}` markup remains unchanged on disk, and the lint still sees exactly the specified classes.
No custom directive or role is installed, and no warning is suppressed.
The stylesheet provides the section 3.4 CSS-clamping fallback for unadapted old notes, with scroll access, hover/focus expansion and unrestricted printing.
Contested and superseded treatments remain visible, and risk/thin classes have distinct border styles.

## Verification notes

The isolated Sphinx test copies the real project configuration, stylesheet and generator into a temporary repository.
It builds the fixture and all five generated pages with warnings treated as errors and checks the rendered old-lesson dropdown's closed state and computed heading.
It also checks that rendering never changes the authored source file.
The root `pyrightconfig.json` selects the repository virtual environment and applies strict checking to this package and `docs/conf.py`.
