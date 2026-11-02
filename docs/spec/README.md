# Content contract specification

This directory is the single source of truth for what a page of the Plone Conference Organizers Handbook looks like and how it is checked.
Three groups of people work from it, usually without ever meeting the author:

- The engineers who build the test harness (task T5) and the convention machinery (task T6). They implement validators and a generator from these files alone.
- The writers and agents who author chapters. They follow the template and the conventions.
- The reviewers who check that chapters and the checks agree.

The spec is complete when a reader who did not write it can build the validators from it without asking a question.
That is the acceptance check for task T2.

The spec files are **not part of the published handbook**.
They are excluded from the Sphinx build (`exclude_patterns`) and appear in no table of contents.

## 1. Reading order

1. This file.
2. [chapter-template.md](chapter-template.md): the fixed nine-section structure and the master chapter list schema.
3. [front-matter.md](front-matter.md): the YAML block at the top of every page.
4. [conventions.md](conventions.md): MUST, DEFAULT and OPTION badges; the lesson, thin and risk admonition blocks; ranking, promotion and contradiction rules; the generated pages; the lint rule catalog.
5. [ledger-schema.md](ledger-schema.md): the evidence rows that lessons trace back to.
6. [governance-sketch.md](governance-sketch.md): the annual ritual, rotation, stewardship proposal and handover deliverables.

Engineers read 3, 4 and 5 line by line.
Chapter authors read 2, 3 and the lesson and level parts of 4.

## 2. The files

| File | Defines | Read by |
|---|---|---|
| [chapter-template.md](chapter-template.md) | Chapter structure, anchors, section purposes and writing rules, maturity minimums, length budget, page kind variants, the chapter contract test (G4). | T5, authors |
| [front-matter.md](front-matter.md) | The front-matter fields, allowed values, validation rules F01 to F09, freshness (G10). | T5, authors |
| [conventions.md](conventions.md) | Normative levels, the stock-admonition field syntax for lessons, thin markers and risks, age ranking, promotion, contradictions, generated pages, lint rules B, L, T, R and N. | T6, T5, authors |
| [ledger-schema.md](ledger-schema.md) | The ledger row schema, the disposition rule (G7), validation rules LD01 to LD11. | T7a to T7f, T5, T6 |
| [chapter-list.yml](chapter-list.yml) | Every page of the handbook: id, title, part, workstream, kind, path, status. | T5, T1, all |
| [handbook-config.yml](handbook-config.yml) | Reference defaults for every tunable: age thresholds, word budget, ID patterns, file locations. | T5, T6 |
| [governance-sketch.md](governance-sketch.md) | The proposal for stewardship and the handover deliverables. | T8, T9, the community |
| [../../tests/scenarios.yml](../../tests/scenarios.yml) | The reader scenarios (G11). | T5, T15 |

## 3. How the pieces fit

```text
 sources (manifest, source IDs S###)
        |
        v
 lessons ledger (rows L-####, each with a disposition)      ledger-schema.md
        |  placed at <chapter id>#<section slug>
        v
 chapters: nine fixed sections, front matter                chapter-template.md, front-matter.md
   - Decisions: MUST / DEFAULT / OPTION badges              conventions.md, section 1
   - Principles: general lessons   (admonition blocks)      conventions.md, section 3
   - Case notes: specific lessons  (admonition blocks)
   - Risks: risk blocks, Thin content: thin blocks          conventions.md, sections 4 and 7
        |
        v
 lint scripts (gates G4, G5, G7, G9)  and  generator        conventions.md, sections 8 and 9
        |
        v
 generated pages: lesson index, risk register, thin registry,
 decision register, coverage map
```

The ID types that tie everything together:

| ID | Example | Defined in |
|---|---|---|
| Source ID | `S042` | The source manifest (task T3). Pattern in the config. |
| Ledger ID | `L-2003` | [ledger-schema.md](ledger-schema.md) |
| Requirement ID | `R-012` | The requirements register (task T4). |
| Chapter id | `finance` | [chapter-list.yml](chapter-list.yml) |
| Anchor | `finance#case-notes` | [chapter-template.md](chapter-template.md), section 2 |

## 4. Reader scenarios

`tests/scenarios.yml` lists at least 15 questions a real organizer asks.
It is written before any chapter exists, so the structure is tested against real needs.

Each scenario has these keys, all required:

| Key | Value |
|---|---|
| `id` | Unique, `S01`, `S02`, and so on. |
| `question` | The reader's question in the reader's words. |
| `target` | A chapter-list `id`, optionally followed by `#<anchor>`. A valid anchor is one of the nine chapter slugs or, for a playbook, one of the four playbook slugs. |
| `max_clicks` | `3`. |

The check (gate G11, task T5):

1. Every `target` id exists in [chapter-list.yml](chapter-list.yml).
2. A target anchor is valid for the kind of the target page.
3. A **click** is one internal link followed in the rendered HTML. Links in the sidebar and in tables of contents count as clicks.
4. Starting at the home page, a breadth-first search over the built site must reach the target page, and the anchor must exist as an element id there, within `max_clicks` clicks.
5. A human re-tests every scenario by reading, before version 1 (task T15).

## 5. Gate map

The plan's gates (section 6.3) and where this spec defines them:

| Gate | What | Defined in |
|---|---|---|
| G1 | Build with zero warnings, no orphan pages | Toolchain (T1); orphans excluded by [front-matter.md](front-matter.md) section 1 |
| G2 | Link check | Toolchain (T1) |
| G3 | Vale and the temporal-word lint | [chapter-template.md](chapter-template.md), section 7 |
| G4 | Chapter contract | [chapter-template.md](chapter-template.md), section 8; [front-matter.md](front-matter.md), section 4 |
| G5 | Directive validation (lesson, thin, risk, level badges) | [conventions.md](conventions.md), section 9 |
| G6 | Manifest integrity | [ledger-schema.md](ledger-schema.md), LD06; manifest owned by T3 |
| G7 | Ledger coverage (every row has a disposition) | [ledger-schema.md](ledger-schema.md), section 5 |
| G8 | Privacy lint | [ledger-schema.md](ledger-schema.md), section 3; [chapter-template.md](chapter-template.md), section 7 |
| G9 | Anchor check | [chapter-template.md](chapter-template.md), section 2 |
| G10 | Scheduled freshness | [front-matter.md](front-matter.md), section 5 |
| G11 | Reader scenarios | Section 4 above |

## 6. Decisions that shaped the spec

- **D6, stock-first.** No custom Sphinx directives or roles. The plan's `{lesson}`, `{thin}` and `{risk}` names denote the conventions in [conventions.md](conventions.md), implemented with stock `{note}` and `{warning}` admonitions, a fixed class, and a one-line field syntax that Python can parse. Badges are stock `sphinx_design` roles. Registries and age badges come from a generator script, checked for drift in CI.
- **D7, generalized information only.** No concrete data enters the handbook: no personal data, no private amounts, no Tito user data. Public prices appear only as dated, sourced examples.
- **D8, stewardship is a proposal.** See [governance-sketch.md](governance-sketch.md).
- **D2, American English.** The handbook is written in American English with one sentence per line and sentence-case headings.

## 7. Changing the spec

1. The spec changes by pull request, like any other file.
2. A change to a field, a vocabulary or a rule updates every file that mentions it in the same commit. The tests in T5 and T6 are the first thing to update.
3. Vocabularies (allowed values) are fixed by the spec tables and not configurable. Tunables are only the keys in [handbook-config.yml](handbook-config.yml).
4. The spec says what is checked; it never says how the scripts are named or laid out. Those are task decisions for T5 and T6.

## 8. Clarifications queued for the spec's next revision

Recorded during the T14 integration pass (2026-11-02). Each line describes practice the version 1 pages follow; the next spec revision should state it in the file named.

1. A badge's `basis:` may cite ledger rows placed in other sections of the same page (adopted practice; conventions.md, section 1).
2. Structural promotion with a stated reason is the accepted route for a general lesson that rests on a single conference; otherwise the prose labels it "candidate, single account" (conventions.md, section 3).
3. Risk and lesson blocks in annexes are not machine-readable, because B05 allows them only in chapters; annex Risks sections are prose (conventions.md, section 2).
4. Case-note titles for Foundation-level ledger rows render `place: n/a` (conventions.md, section 3.3).
5. The survey template carries twelve placed rows; L-1020 and L-4209 predate the 2026 survey (ledger-schema.md, placement).
6. L-1036 is placed at `cost-benchmarks` and cited from `budget-sheet-template` by pointer only (ledger-schema.md, placement).
7. The generated lessons-ledger page is excluded from the temporal-word lint as a verbatim data dump (chapter-template.md, section 7).
8. The CC BY-SA 4.0 share-alike question on the Seattle 2006 digest paraphrases stays open for the T3/D5 publication audit; it is also recorded on the honesty-statement page.
