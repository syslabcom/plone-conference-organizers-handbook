# Chapter template

Every chapter of the handbook is one page with the same structure.
A reader who knows one chapter knows where to look in all of them.
The contract test (gate G4, task T5) enforces the structure described here.

Related files:
[README](README.md) · [front matter](front-matter.md) · [conventions](conventions.md) · [ledger schema](ledger-schema.md) · [chapter list](chapter-list.yml)

## 1. Master chapter list

[chapter-list.yml](chapter-list.yml) is the single list of every page the handbook will contain.
It is machine-readable, and the tests read it.

Each entry has these keys, all required:

| Key | Value |
|---|---|
| `id` | Unique slug: lowercase letters, digits and hyphens, starting with a letter. It is used in anchors, ledger dispositions, scenario targets and playbook links. |
| `title` | Human title in sentence case. The page's H1 must equal it exactly. |
| `part` | `"0"` to `"5"`, or `"appendices"`. |
| `workstream` | Grouping slug. For Part 2 it is the workstream group; for other parts it names the part. |
| `kind` | `chapter`, `page`, `playbook`, `annex`, `appendix` or `generated` (section 6). |
| `path` | Repo-relative path of the Markdown file. Always starts with `docs/`. |
| `status` | `planned` or `written`. |

Rules:

1. An entry with `status: planned` is an expected failure (`xfail(strict=True)`) in the contract test.
2. The commit that writes the page sets `status: written` and removes the xfail in the same commit. An unexpected pass fails the build.
3. Adding a chapter means adding an entry first. Nobody writes a page that is not in the list.
4. Splitting a chapter (section 5) adds entries with ids of the form `<parent-id>-<subtopic>`, the same `workstream` and `part`, and `status: planned`. The parent stays as the overview page.
5. Only entries with `kind: chapter` use the nine-section template in section 2. Other kinds use the variants in section 6.

## 2. Fixed structure

A `chapter` page has this shape, top to bottom:

1. YAML front matter (section 3 below, [front matter](front-matter.md)).
2. One H1 equal to the chapter-list `title`.
3. Exactly nine H2 sections, with exactly these headings, in exactly this order.
4. Nothing after section 9.

| No. | H2 heading (exact text) | Anchor slug | Diataxis type |
|---|---|---|---|
| 1 | Why it matters | `why-it-matters` | explanation |
| 2 | Applies when | `applies-when` | reference |
| 3 | Decisions you must make | `decisions-you-must-make` | reference |
| 4 | How-to | `how-to` | how-to |
| 5 | Principles and general lessons | `principles-and-general-lessons` | explanation |
| 6 | Case notes | `case-notes` | experience report |
| 7 | Risks | `risks` | reference |
| 8 | Thin content | `thin-content` | reference |
| 9 | Sources and further reading | `sources-and-further-reading` | reference |

The plan counts the front matter as item 10 of the template.
It is listed last there because it is metadata, but it sits first in the file.

Headings below H2 are allowed inside a section (H3 only).
H4 and deeper are not used.
Headings are sentence case.

### Anchors

An anchor is `<id>#<slug>` where `<id>` is a chapter-list id and `<slug>` is one of the nine slugs above.
Slugs are the lowercase heading with non-alphanumeric runs replaced by single hyphens, which is what the MyST heading-anchor generation produces.
For playbooks the valid slugs are in section 6.2.
Scenario targets, ledger dispositions and the T-minus checklist cite anchors in this form.
The anchor check (gate G9) resolves them against the chapter list and the slug sets.

## 3. Section by section

### 3.1 Why it matters (explanation)

**Purpose.** Tell the reader what this topic is for, who is affected, and what goes wrong without it.

**Writing rules.**

1. Two to five short paragraphs. No lists, no badges, no lesson blocks.
2. Open with the organizer's problem, not with a definition.
3. Name the stakeholders touched (Foundation, community, sponsors, venue, volunteers) where relevant.
4. State consequences in plain terms. Money, time and trust are the three currencies.
5. Link to the how-to section instead of repeating procedures.
6. Any figure needs an as-of date and a source ID.

### 3.2 Applies when (context dimensions)

**Purpose.** Show which conferences this chapter fits, so a team can decide whether to adopt, adapt or skip it.

**Writing rules.**

1. A bullet list. Each bullet starts with one context token in backticks, then one sentence saying why.
2. The tokens use the vocabulary in [conventions](conventions.md), section 3.5, for example `` `size=medium,large` `` or `` `jurisdiction=NL` ``.
3. A chapter that applies to every conference has exactly one bullet: `` `all` ``.
4. A bare dimension name, for example `` `jurisdiction` ``, means the chapter applies to all values and its content varies by that dimension.
5. The set of tokens in the bullets must equal the front-matter `applies-to` list exactly (gate G4).
6. The generator and the Tailoring Record template read this section.

### 3.3 Decisions you must make

**Purpose.** List the choices an organizer has to make, with the normative level of the advice, so a team can record its choices.

**Writing rules.**

1. One top-level bullet per decision, in the grammar of [conventions](conventions.md), section 1.4: level badge, bold question, guidance, optional `(decide-by: T-...)`.
2. Every top-level bullet carries exactly one badge: MUST, DEFAULT or OPTION.
3. MUST items cite the requirements register with an as-of date. DEFAULT items cite at least two ledger IDs from two conferences.
4. Phrase each decision as a question the team can answer yes, no or with a name.
5. Order decisions by when they must be made, earliest first.
6. Guidance is one to three sentences. Procedure belongs in section 4.
7. The generator collects these bullets into the decision register.

### 3.4 How-to (playbook)

**Purpose.** Give a practical playbook a competent organizer can follow, assuming they have made the decisions in section 3.

**Writing rules.**

1. Numbered steps in imperative voice. One action per step.
2. Group steps in H3 phases when there are more than seven steps, for example by T-minus window.
3. Each step says what done looks like. Name the artifact or the confirmation.
4. Optional badges per step ([conventions](conventions.md), section 1.3).
5. Reference templates in the appendices by link. Never paste a template into a chapter.
6. No history, no anecdotes. Those belong in section 6.
7. Costs and prices appear only as dated, sourced examples, never as rules.

### 3.5 Principles and general lessons

**Purpose.** State the timeless advice that holds across conferences, years and places.

**Writing rules.**

1. General lessons only: lesson blocks with `scope: general` ([conventions](conventions.md), section 3).
2. A general lesson passes the promotion rule: three independent conferences across two organizing bodies, or a structural reason independent of year.
3. General lessons are never dated and never name a place or organizer.
4. Plain prose principles are allowed between lesson blocks, but a claim that rests on evidence is a lesson block, not prose.
5. Order the lesson blocks by first ledger ID ascending.
6. If nothing qualifies yet, write one sentence saying so and add a thin marker in section 8. Do not promote early.

### 3.6 Case notes (specific lessons, newest first, age-badged)

**Purpose.** Preserve what individual conferences learned, with enough provenance for the reader to judge how far it travels.

**Writing rules.**

1. Specific lessons only: lesson blocks with `scope: specific`. Each has a year, a place, an organizing body, a source ID and a ledger ID.
2. Newest first: `year` descending, then confidence (observed, reported, hearsay), then first ledger ID.
3. The block title and classes are computed (the age badge). Never type them by hand; run the generator's write mode.
4. One lesson per block. Keep each under 80 words.
5. State what happened and in what context. Add a `context` field when the lesson depends on size, jurisdiction or format.
6. No personal data and no private amounts (D7). Generalize.
7. A specific lesson never lives outside this section.
8. If no case note qualifies yet, write one sentence saying so and add a thin marker in section 8.

### 3.7 Risks

**Purpose.** Record what can go wrong in this workstream and what reduces the likelihood or the impact.

**Writing rules.**

1. Risk blocks ([conventions](conventions.md), section 7), or the exact sentence `No chapter-specific risks recorded. Rationale: <one sentence>.`
2. Each risk is one thing that can go wrong, phrased as an event, not a worry.
3. Likelihood and impact are low, medium or high. Judge them for a typical mid-size conference and say so in the body if the judgment depends on size.
4. The mitigation is one sentence and names an action, not an attitude.
5. Link a `playbook` when one exists in Part 3. Do not restate the playbook here.
6. Do not duplicate advice that is in the how-to. Link to it.

### 3.8 Thin content (markers or an explicit "none known")

**Purpose.** Say, in public, where this chapter is weak, so readers can calibrate trust and contributors can help.

**Writing rules.**

1. Thin blocks ([conventions](conventions.md), section 4), or the exact sentence `None known as of YYYY-MM-DD.`
2. A stub chapter must have at least one thin block.
3. Name what would close the gap in `needs`, and who might know in `who-might-know` (roles and groups, never private persons).
4. Use the `area` field when the gap belongs to one of the ten predicted thin areas.
5. This section is never empty and never deleted.

### 3.9 Sources and further reading

**Purpose.** Let a reader verify every claim and find more.

**Writing rules.**

1. A bullet list. Each source bullet starts with a source ID token (`S042`) and a short citation.
2. Every source ID used anywhere on the page (in lesson `source` fields, in prose or in badges) appears in this list.
3. Every source ID must exist in the source manifest. Archived copies are linked from the generated bibliography, not from here.
4. An optional H3 "Further reading" holds external links that have no source ID. Each carries an as-of date.
5. Pointers to related chapters are allowed. Pointers to private material are not.

## 4. Maturity expectations

The `maturity` field ([front matter](front-matter.md)) states how far a page has come.
The contract test checks these minimums.

| Maturity | Structure | Evidence | Review |
|---|---|---|---|
| `stub` | All nine sections present. Content may be one paragraph each. At least one thin block. | None required. | None. |
| `draft` | All nine sections have real content. | At least one source. | None. |
| `reviewed` | As `draft`. | At least two distinct source IDs. A named steward (not `unassigned`). | A reviewer other than the author checked it. |
| `proven` | As `reviewed`. | At least three distinct source IDs. | An organizing team used it in a real conference and the Tailoring Record or case file cites it. |

Maturity changes are recorded in the changelog.
A page never claims more than its evidence supports (gate in task T14).

## 5. Length budget

A chapter holds at most 2500 words (config key `word-budget`).
Above that it must split.

Counting rules:

1. Count whitespace-separated tokens in the Markdown body after the front matter.
2. Exclude fenced code blocks that are not admonitions, and MyST comment lines (`%`).
3. Include admonition text, list text and headings.
4. Exclude section 9 (Sources and further reading).

When a chapter hits the limit, split along a natural seam, for example `finance` into `finance` (overview, decisions) and `finance-vat-regimes`.
Add the new entry to [chapter-list.yml](chapter-list.yml) first (section 1, rule 4), move content, and leave links behind.

## 6. Variants for other page kinds

Only `chapter` pages use the nine-section template.
All other kinds carry front matter (see [front matter](front-matter.md)) and an H1 equal to the chapter-list title.

### 6.1 `page`

Free structure, headings in sentence case, H2 and H3 only.
Used for Part 0, Part 3 method pages, Part 4 and the Part 5 pages that are authored.
Lesson, thin and risk blocks follow the placement table in [conventions](conventions.md), section 2.3.
The `cross-cutting-risks` page may hold risk blocks anywhere.

### 6.2 `playbook`

Incident playbooks in Part 3 have exactly these H2 sections, in this order:

| No. | H2 heading | Anchor slug | Content |
|---|---|---|---|
| 1 | Triggers | `triggers` | The observable events that start this playbook. A bullet list. |
| 2 | First-hour actions | `first-hour-actions` | Numbered steps for the first hour. |
| 3 | Owner roles | `owner-roles` | A table: role, responsibility. Roles, never persons. |
| 4 | Related chapters | `related-chapters` | Links to the chapters that hold the full advice. Each link resolves to a chapter-list id. |

A playbook links to chapters and never restates them.
A playbook has no lesson blocks.

### 6.3 `annex`

Jurisdiction annexes and variant annexes.
The first lines after the H1 are the disclaimer: `This annex is general information, not legal, tax or insurance advice. Check current rules with a qualified local adviser.`
Annexes start as stubs with thin markers (`area: jurisdiction-annexes`).
Front matter carries the optional `jurisdiction` field.

### 6.4 `appendix`

Templates, the T-minus checklist, the glossary and the annotated digest.
Free structure.
Templates must not contain real names, amounts or contacts (D7).
Every file under `_static/templates/` is referenced from at least one page.

### 6.5 `generated`

Written only by the generator ([conventions](conventions.md), section 8).
Humans never edit them.
They carry minimal front matter (`diataxis` and `myst` only) and are exempt from the steward, deputy, review-by and maturity checks.
The generated header comment is the first line after the front matter.

## 7. Writing rules for all pages

1. American English.
2. One sentence per line in the Markdown source.
3. Sentence-case headings.
4. No temporal words ("currently", "recently", "this year", "soon", "new") without a dated anchor. Write "as of 2026-11".
5. Prices, tax rates and fees appear only as dated, sourced examples.
6. Only generalized information, rules, guidelines, risks and pointers enter the handbook. No concrete personal data, no private amounts, no Tito user data (D7).
7. The handbook is advisory. It is not Foundation policy and not legal advice.
8. No exclamation marks. Plain words over hype.
9. Prefer commas and periods over dashes.

## 8. Contract test summary (gate G4)

For each chapter-list entry with `status: written` and `kind: chapter`, the test asserts:

1. The file exists at `path`, has valid front matter ([front matter](front-matter.md)), and one H1 equal to `title`.
2. Exactly the nine H2 headings of section 2, exact text and order, and no H4 or deeper.
3. Section 2 tokens equal `applies-to`.
4. Section 3 bullets pass N01, section 7 passes R03 and section 8 passes T02 ([conventions](conventions.md), section 9).
5. Every source ID on the page is listed in section 9 and exists in the manifest.
6. The word count is at most `word-budget`.
7. The maturity minimums of section 4 hold.

For entries with `status: planned` the same test is `xfail(strict=True)`.
For other kinds the test asserts the rules of section 6 that apply.

## 9. Copy-paste skeleton

````markdown
---
steward: unassigned
deputy: unassigned
review-by: 2027-11-01
maturity: stub
applies-to: [all]
diataxis: mixed
myst:
  html_meta:
    "description lang=en": "One sentence, 50 to 160 characters, saying what this chapter helps an organizer decide."
    "keywords": "Plone, Plone Conference, organizing, <topic>"
---

# Chapter title

## Why it matters

## Applies when

- `all` Applies to every Plone conference.

## Decisions you must make

- {bdg-secondary}`OPTION` **Decision as a question?** One to three sentences. (decide-by: T-6m)

## How-to

1. Do one thing.

## Principles and general lessons

No general lesson has passed the promotion rule yet.

## Case notes

## Risks

No chapter-specific risks recorded. Rationale: not yet analyzed.

## Thin content

```{warning} Chapter not yet written
:class: hb-thin hb-thin-gap
thin | kind: gap | needs: A first draft from ledger evidence | who-might-know: Conference Committee; past organizers

Stub created from the chapter list.
```

## Sources and further reading

- S000 Replace with a real source ID.
````
