# T10 verification record

## Output inventory

| Chapter-list ID | Path | Rendered evidence |
|---|---|---|
| `conference-index` | `docs/evidence/conference-index.md` | 24 year entries, 2003–2026 |
| `conference-data-table` | `docs/evidence/conference-data-table.md` | 24 year rows citing 38 placed ledger rows |
| `cost-benchmarks` | `docs/evidence/cost-benchmarks.md` | 3 dated, sourced cost observations |
| `source-bibliography` | `docs/evidence/source-bibliography.md` | 82 linked sources and 23 held-back notices |
| `lessons-ledger` | `docs/evidence/lessons-ledger.md` | 722 rows, sorted by ledger ID |

The 23 held sources comprise 11 explicit exclusions and 12 internal-2026 sources without audit rows.
Their archive files and original URLs are absent from the rendered bibliography.
The ledger reproduces screened derivative evidence and links source IDs to bibliography metadata.

## Final drift and fixture-test transcript

```text
$ venv/bin/python -m pytest scripts/evidence/tests/ -q
.......                                                                  [100%]
7 passed in 0.36s
$ venv/bin/python scripts/evidence/build_evidence.py --check
Sources: 82 rendered, 23 held back; ledger: 722; conference years: 24; table evidence: 38; cost rows: 3
PASS evidence pages match regeneration
```

Both commands exited 0.
The tests include a doctored-page check that exits 1 without rewriting the page, and a repaired-page check that exits 0 after regeneration.

## Real-repository convention and manifest transcript

```text
$ venv/bin/python -m pytest tests/test_g5_conventions.py tests/test_g6_manifest.py -q
.................................                                        [100%]
33 passed in 0.65s
```

Exit 0; no findings name a generated evidence page.

## Strict Sphinx build transcript

```text
$ make html SPHINXOPTS="-W --keep-going"
Running Sphinx v8.2.3
...
docs/evidence/conference-index.md: WARNING: document isn't included in any toctree [toc.not_included]
...
docs/risk/playbooks/cash-flow-crunch.md:33: WARNING: 'myst' cross-reference target not found: 'low-ticket-sales.md' [myst.xref_missing]
docs/risk/playbooks/cash-flow-crunch.md:57: WARNING: 'myst' cross-reference target not found: 'low-ticket-sales.md' [myst.xref_missing]
...
build finished with problems, 22 warnings (with warnings treated as errors).
make: *** [html] Error 1
```

The `make` command exited 2.
This is a failed strict build, not a zero-warning result.
Of the 22 warnings, one names the conference index, 19 are missing toctree parents for other workstreams, and two are unresolved links on the cash-flow playbook.
The evidence index has a toctree for its four sibling outputs, so only that index needs a parent entry for this workstream.
The task forbids editing the root index or another agent's navigation pages.
No orphan metadata, custom directives or warning suppressions were introduced.

The build copied 82 permitted archive downloads.
No warning named a bibliography download, evidence footnote or evidence cross-reference.

## Static checks and implementation review

Language-server error diagnostics are clean for all five Python files.
Every Python file parses, and each is below 200 nonblank, noncomment lines.

Responsibilities are separated into input models, MyST rendering, the CLI and fixture tests.
The typed parser interfaces describe repository-owned YAML/JSON documents; the existing gates own full schema validation.
No new dependency, custom directive, logging framework, type-ignore or cast was introduced.
Renderers preserve conflicting evidence instead of choosing an inferred attendance total.
Tests exercise real CLI file behavior and hold suppression without mocks.

## Integration work outside this task's permissions

1. Attach `evidence/conference-index` to a root-reachable toctree, alongside the other agents' navigation integration.
2. Change the five chapter-list entries from `planned` to `written` during integration.
3. Supply audit recommendations for internal sources S098–S109 before enabling archive links.
4. Resolve the cost-page placement gap: only three rows are placed there, with no Bristol proportions or dated fee rows.

The final inputs differ from the task's source count: 105 unique manifest IDs exist, versus 93 audit rows.
The two authored-kind pages retain draft maturity and the requested 2028-11-02 review date; generated-kind pages follow the spec's minimal-front-matter exemption.
There is no separate ranking-rule chapter-list entry to generate.

The reusable integration lesson is recorded in the generator README: a locally complete evidence subtree still requires a root-reachable parent, and planned entries require the integrator's status change.
