# Conventions: normative levels, lessons, thin content, risks

This file defines every convention the handbook adds on top of plain MyST Markdown.
Decision D6 governs the implementation: only stock MyST syntax and the extensions that `plone/documentation` already uses (`myst_parser`, `sphinx_design`).
There are no custom Sphinx directives or roles.
Everything below is therefore a **text convention** that Python lint scripts validate and a generator script turns into registries.
The lint scripts and the generator are built in task T6 from this file alone.
The chapter-level gates that call them are built in task T5.

Related files:
[README](README.md) · [chapter template](chapter-template.md) · [front matter](front-matter.md) · [ledger schema](ledger-schema.md) · [governance sketch](governance-sketch.md) · [config defaults](handbook-config.yml) · [chapter list](chapter-list.yml)

Decision D7 applies to everything in this file: only generalized information, rules, guidelines, risks and pointers enter the handbook, never concrete data.
No block, field or example may carry personal data, private amounts, contact details or Tito user data.

## 1. The three normative levels

Every decision item (and optionally other checklist items, see section 1.3) carries exactly one badge.
The badge is a stock `sphinx_design` inline role.
The word is part of the badge text, so color is never the only signal.

### 1.1 Exact markup

| Level | Markup (copy exactly) |
|---|---|
| MUST | ``` {bdg-danger}`MUST` (req: R-012; as-of: 2026-11-02) ``` |
| DEFAULT | ``` {bdg-primary}`DEFAULT` (basis: L-2001, L-3004) ``` |
| OPTION | ``` {bdg-secondary}`OPTION` ``` |

Leading and trailing spaces in the table are not part of the markup.
The IDs and the date in the table are placeholders.
The grammar, as Python regular expressions applied to the text of a list item or paragraph after the list marker, is:

```text
MUST     ^\{bdg-danger\}`MUST` \(req: (?P<req>R-[0-9]{3}); as-of: (?P<asof>[0-9]{4}-[0-9]{2}-[0-9]{2})\)
DEFAULT  ^\{bdg-primary\}`DEFAULT` \(basis: (?P<basis>L-[0-9]{4}(, L-[0-9]{4})+)\)
OPTION   ^\{bdg-secondary\}`OPTION`
```

The ID patterns come from [the config](handbook-config.yml) (`requirement-id-pattern`, `ledger-id-pattern`).
The regular expressions above show the default patterns.

### 1.2 Semantics

| Level | Meaning | What the badge must carry | What deviation takes |
|---|---|---|---|
| MUST | A Foundation requirement or a legal necessity. | `req:` is a row ID in the Foundation requirements register (task T4). `as-of:` is the date that row was last verified. | A written Foundation exception, linked in the team's Tailoring Record. Legal necessities cannot be waived by the handbook. |
| DEFAULT | A strong recommendation backed by several conferences. | `basis:` lists at least two ledger IDs that come from at least two distinct conferences (distinct year and place pairs). | A recorded reason in the team's Tailoring Record. |
| OPTION | Context-dependent; the team chooses. | Nothing. | Nothing. This is a free choice. |

Rules the lint enforces:

1. A MUST badge cites a register row that exists in the requirements register file named in the config (`paths.requirements-register`).
2. The `as-of` date in the badge equals the `as-of` date of that register row.
   When T4 re-verifies a row, every badge citing it fails until it is updated. This is intended.
3. The cited register row has status `verified-current` or `verified-changed`.
   A row with status `unverifiable` cannot back a MUST; the item becomes a DEFAULT with a thin marker.
4. A DEFAULT badge cites at least two ledger IDs that exist and whose rows come from at least two distinct conferences.
   A recommendation with weaker evidence is an OPTION, and the chapter says why in prose.
5. An OPTION badge has no parenthesis.

### 1.3 Placement

1. A badge is the first inline content of a list item or of a paragraph.
   A badge never appears in a heading, a table cell, an admonition title or a lesson body.
2. Badges are allowed only in chapter sections 3 (Decisions you must make), 4 (How-to) and 5 (Principles and general lessons).
3. Every top-level list item in section 3 carries exactly one badge.
   In sections 4 and 5 badges are optional, and a list item carries at most one.
4. Pages of kind `page`, `playbook`, `annex` and `appendix` may use badges in any section; nothing requires them.

### 1.4 Decision items (section 3)

Section 3 holds a top-level bullet list.
Each bullet follows this grammar, so the generator can build the decision register:

```text
- <badge> **<decision phrased as a question?>** <one or more sentences of guidance> (decide-by: T-<n><unit>)
```

- `<badge>` is one of the three level badges from section 1.1.
- The bold span is the decision; the generator reads the first bold span in the bullet.
- `(decide-by: ...)` is optional. `<unit>` is `d` (days), `w` (weeks) or `m` (months). Example: `(decide-by: T-6m)`. It is relative to the first conference day.
- Indented sub-bullets and continuation lines belong to the same decision.

Example:

````markdown
- {bdg-primary}`DEFAULT` (basis: L-2001, L-3004) **Who sells the ticket?** Name the selling entity before pricing, because the selling entity decides the VAT regime. (decide-by: T-9m)
````

## 2. Stock admonition blocks

Lessons, thin markers and risks are MyST admonitions: the stock `{note}` and `{warning}` directives, a fixed `:class:` option, and one fixed **field line** as the first body line.
Nothing else is required to render them. The generator and lint add rigor on top.

### 2.1 Block grammar

```text
<fence>{<directive>} <title>
:class: <class> <class> ...
<field line>

<body, free Markdown>
<fence>
```

- `<fence>` is three or more backticks. The closing fence has the same number of backticks. Use more backticks on the outer fence if the body contains a code fence. Colon fences (`:::`) are not used for managed blocks.
- `<directive>` is `note` for lessons and `warning` for thin markers and risks.
- `<title>` is the directive argument on the opening line. For lessons it is generated (section 3.3). For thin markers and risks the author writes it: 1 to 80 characters, no backticks.
- The only allowed option is `:class:`, on the line immediately after the opening line. The class tokens identify the block kind and carry the computed state.
- The **field line** is the first non-blank line after the options. It is also the first line of the admonition body, and it renders as visible text. That visible line is the provenance strip a reader sees.
- A blank line follows the field line, then the free-Markdown body.

### 2.2 Field-line grammar

A field line is one physical line (no wrapping) of this form:

```text
<kind> | <key>: <value> | <key>: <value> | ...
```

Parse it in exactly these steps:

1. Strip the line.
2. Split on the separator ` | ` (space, pipe, space). A value therefore must not contain that sequence.
3. The first segment is the block kind: `lesson`, `thin` or `risk`. It must equal the kind implied by the `:class:` option.
4. For every other segment, split at the first colon. The part before is the key, the part after (stripped) is the value.
5. A key matches `[a-z][a-z-]*`. A value is non-empty. A key may appear only once. Only keys listed for the kind are allowed.
6. List values (marked "list" below) are comma-separated; strip every item. Empty items are errors.

A minimal reference parser:

```python
import re

SEP = " | "

def parse_field_line(line: str) -> tuple[str, dict[str, str]]:
    parts = line.strip().split(SEP)
    kind, fields = parts[0], {}
    for part in parts[1:]:
        key, sep, value = part.partition(":")
        key, value = key.strip(), value.strip()
        if not (sep and re.fullmatch(r"[a-z][a-z-]*", key) and value):
            raise ValueError(f"bad field segment: {part!r}")
        if key in fields:
            raise ValueError(f"duplicate key: {key}")
        fields[key] = value
    return kind, fields
```

### 2.3 Where a block may appear

The `kind` in [chapter-list.yml](chapter-list.yml) is the page kind.

| Block | Allowed in page kind | Allowed in section | Notes |
|---|---|---|---|
| lesson, `scope: general` | `chapter` | 5. Principles and general lessons | Never dated. |
| lesson, `scope: specific` | `chapter` | 6. Case notes | A specific lesson anywhere else fails the build. |
| thin | `chapter` | 8. Thin content | In `page`, `annex` and `appendix` kinds a thin block may appear anywhere. |
| risk | `chapter` | 7. Risks | The page `cross-cutting-risks` may also hold risk blocks anywhere. |

Blocks inside any other fenced block (for example the examples in this file) are text, not managed blocks.
The parser tracks fences from the top of the file; a managed block is recognized only when its opening fence is not inside another fence.

## 3. Lessons

A lesson is one transferable statement with its provenance.
There are two scopes.
General lessons are timeless claims that passed the promotion rule (section 5).
Specific lessons are claims from one conference at one time and place.

### 3.1 Block markup

````markdown
```{note} [specific · 2012 · Arnhem · 14 y] stale-prone
:class: hb-lesson hb-specific hb-age-old hb-stale-prone
lesson | scope: specific | year: 2012 | place: Arnhem | org: Four Digits | source: S042 | ledger: L-2003 | confidence: observed | status: active

The organizers ran the registration desk with one more volunteer than planned and never had a queue.
```
````

This example is illustrative: the text is not evidence.
A general lesson:

````markdown
```{note} [general]
:class: hb-lesson hb-general
lesson | scope: general | source: S042, S077, S101 | ledger: L-2003, L-3004, L-4010 | confidence: reported | status: active | basis: independent-conferences

Close the program before opening registration, because speakers' ticket choices depend on it.
```
````

### 3.2 Fields

| Key | Applies to | Required | Value |
|---|---|---|---|
| `scope` | all | yes | `general` or `specific` |
| `year` | specific | yes; forbidden on general | Integer, 2000 up to `as-of-year` |
| `place` | specific | yes; forbidden on general | City or place name, 1 to 40 characters |
| `org` | specific | yes; forbidden on general | Organizing body that ran that conference, 1 to 60 characters. Organizations only, never a person. |
| `source` | all | yes | List of source IDs (`source-id-pattern`) |
| `ledger` | all | yes | List of ledger IDs (`ledger-id-pattern`) |
| `confidence` | all | yes | `observed`, `reported` or `hearsay` |
| `status` | all | yes | `active`, `contested` or `superseded` |
| `basis` | general | yes; forbidden on specific | `independent-conferences` or `structural` |
| `reason` | general with `basis: structural` | yes in that case; otherwise forbidden | One sentence, at most 200 characters, naming the structural reason (for example a legal rule) |
| `context` | all | no | Context tokens, see section 3.5 |
| `issue` | all | yes when `status: contested`; otherwise forbidden | `#<n>` or `https://github.com/<owner>/<repo>/issues/<n>` |
| `by` | all | yes when `status: superseded`; otherwise forbidden | One ledger ID of the lesson that replaces this one |
| `conflicts-with` | all | no | List of ledger IDs of lessons this one is known to contradict (section 6) |

### 3.3 Computed title and classes

The title and the class tokens are derived from the fields.
Authors do not type them by hand: the generator's write mode (`fix`) writes them and the lint compares them.
Task T6 decides the script names; the contract is the pure function below.

```python
def age_bucket(age: int, recent_max: int = 3, mid_max: int = 8) -> str:
    if age <= recent_max:
        return "recent"
    if age <= mid_max:
        return "mid"
    return "old"

def lesson_title(f: dict, as_of_year: int) -> str:
    if f["scope"] == "general":
        base = "[general]"
        suffixes = []
    else:
        age = as_of_year - int(f["year"])
        base = f"[specific · {f['year']} · {f['place']} · {age} y]"
        suffixes = ["stale-prone"] if age_bucket(age) == "old" else []
    if f["status"] != "active":
        suffixes.append(f["status"])
    return " ".join([base, *suffixes])

def lesson_classes(f: dict, as_of_year: int) -> set[str]:
    classes = {"hb-lesson", f"hb-{f['scope']}"}
    if f["scope"] == "specific":
        bucket = age_bucket(as_of_year - int(f["year"]))
        classes.add(f"hb-age-{bucket}")
        if bucket == "old":
            classes.add("hb-stale-prone")
    if f["status"] != "active":
        classes.add(f"hb-{f['status']}")
    return classes
```

The separator inside the badge is the middle dot ` · ` (U+00B7) with a space on each side.
The age is whole years: `as-of-year` minus `year`, where `as-of-year` comes from [the config](handbook-config.yml) and is pinned, not read from the clock.
This keeps builds reproducible. The pin is bumped at each annual release.

Rendered title examples with `as-of-year: 2026`:

| Fields | Title |
|---|---|
| general, active | `[general]` |
| specific, 2024, Utrecht | `[specific · 2024 · Utrecht · 2 y]` |
| specific, 2018, Tokyo | `[specific · 2018 · Tokyo · 8 y]` |
| specific, 2012, Arnhem | `[specific · 2012 · Arnhem · 14 y] stale-prone` |
| specific, 2012, Arnhem, contested | `[specific · 2012 · Arnhem · 14 y] stale-prone contested` |

Lint rule: the directive title must equal `lesson_title(...)` exactly, and the class set must equal `lesson_classes(...)`.
Unknown extra classes are errors.

### 3.4 Age ranking

Ranking is computed, never hand-written.

1. **General outranks specific.**
2. Within specific, the bucket is `recent` (age 0 to 3), `mid` (4 to 8) or `old` (more than 8).
   The two thresholds are `age-thresholds.recent-max-age` and `age-thresholds.mid-max-age` in the config.
3. Rank values: general 0, recent 1, mid 2, old 3.

Orderings that follow from the rule, enforced by lint:

- **Case notes (section 6)** list specific lessons by `year` descending, then by confidence (`observed` before `reported` before `hearsay`), then by the first ledger ID ascending.
- **Principles (section 5)** list general lessons by the first ledger ID ascending.

Rendering requirements:

- The block renders as a stock admonition with the computed title as its heading.
- The class tokens are the styling hooks. T6 supplies CSS for them:

| Class | Required styling intent |
|---|---|
| `hb-general` | Strongest emphasis of the lesson classes. |
| `hb-age-recent` | Normal emphasis. |
| `hb-age-mid` | Reduced emphasis. |
| `hb-age-old`, `hb-stale-prone` | Weakest emphasis, and the body rendered collapsed or visually clamped. The `stale-prone` word in the title is the non-visual signal. If the theme offers no collapse mechanism, clamping the body with CSS is enough. |
| `hb-contested`, `hb-superseded` | A visible status treatment. A superseded lesson is struck through or dimmed. |

The generator produces the **lesson index** page (section 8.1), which lists every lesson in rank order within its chapter.

### 3.5 Context tokens

The `context` field and the front-matter `applies-to` field share one vocabulary.
A context is a list of tokens separated by `; `.
A token is `<dimension>=<value>[,<value>...]`.

| Dimension | Allowed values |
|---|---|
| `size` | `small` (up to 150 attendees), `medium` (150 to 400), `large` (more than 400) |
| `jurisdiction` | An ISO 3166-1 alpha-2 country code, or `EU` |
| `organizer` | `company`, `volunteer-group`, `foundation-led`, `mixed` |
| `budget` | `seed-loan`, `financial-agent`, `own-risk` |
| `venue` | `hotel`, `university`, `conference-center`, `mixed` |
| `format` | `in-person`, `hybrid`, `online` |
| `language` | An ISO 639-1 language code |

Two contexts **distinguish** each other when some dimension appears in both and the value sets are disjoint.
An absent `context` means "all contexts".

Example: `context: size=small; jurisdiction=NL,BE`.

### 3.6 Writing rules for the lesson body

1. One lesson, one statement. If the body needs the word "and" to join two lessons, split it.
2. Write the transferable statement first, then at most a short reason.
3. No names of private persons, no contact details, no raw amounts from private books (D7).
   A public price may appear only with an as-of date and a source, for example "the platform charged 2.89 EUR per Stripe-paid ticket as of 2026-11".
4. A specific lesson states what happened and where it applies. It never begins "always" or "never".
5. Keep it under 80 words. Longer material belongs in the chapter's how-to or in the source.

## 4. Thin content

A thin marker says, in public, where the handbook is weak.
A stub with a thin marker is better than a missing chapter.

### 4.1 Block markup

````markdown
```{warning} Visa guidance outside the Schengen area
:class: hb-thin hb-thin-gap
thin | kind: gap | needs: Current visa-letter practice for two non-Schengen host countries | who-might-know: Foundation travel-support role; past organizers outside Europe | area: non-eu-legal-tax-visa | issue: #14

No evidence beyond a dated North American account is archived.
```
````

### 4.2 Fields

| Key | Required | Value |
|---|---|---|
| `kind` | yes | `gap`, `single-source` or `stale` |
| `needs` | yes | What evidence or contribution would close the gap, one sentence |
| `who-might-know` | yes | Roles, groups or public organizations. Never a private person's name or contact (D7). |
| `area` | no | One of the ten predicted thin areas below, or `other` |
| `issue` | no | `#<n>` or a full GitHub issue URL. The optional "help wanted" script writes it back. |
| `since` | no | ISO date the marker was placed |

Kinds:

| Kind | Meaning |
|---|---|
| `gap` | No evidence located. |
| `single-source` | Exactly one source or one conference supports the content. |
| `stale` | Evidence exists but is older than the `old` threshold or known to be outdated. |

Allowed `area` values (the ten predicted thin areas of the plan, section 9):
`hybrid-online`, `accessibility`, `non-eu-legal-tax-visa`, `sponsorship-down-market`, `pricing-elasticity`, `small-budget`, `health-safety`, `sustainability`, `jurisdiction-annexes`, `post-mortem-2026`, and `other`.

Classes: `hb-thin` plus `hb-thin-<kind>`. The class set must match exactly.
The title is author-written and names the thin topic.

### 4.3 The Thin content section

Section 8 of every chapter contains either at least one thin block or exactly this one-line sentence:

```text
None known as of YYYY-MM-DD.
```

The date is a real ISO date. A stub (maturity `stub`) must contain at least one thin block.
The generator produces the **thin registry** page (section 8.3).
Combined with each page's `maturity`, it produces the **coverage map**.

## 5. The promotion rule (specific becomes general)

A lesson with `scope: specific` may be restated as a lesson with `scope: general` only when one of these holds:

1. **Independent evidence.** The ledger rows cited by the general lesson come from at least 3 independent conferences and at least 2 organizing bodies.
   Independent conferences means 3 distinct (year, place) pairs.
   Two organizing bodies means 2 distinct `org` values (compared after trimming and case folding).
   The lesson carries `basis: independent-conferences`.
2. **Structural reason.** The lesson rests on a reason that does not depend on the year, for example a legal rule or a physical constraint.
   The lesson carries `basis: structural` and a `reason` field.

Lint enforces both: for `basis: independent-conferences` it loads the cited ledger rows and counts distinct (year, place) pairs and distinct `org` values.
Promotions are recorded in the changelog (one line: the general lesson's ledger IDs and the date).
The general lesson replaces the specific ones in the page; the specific ones stay in the ledger.

## 6. The contradiction rule

Two lessons with `status: active` may not conflict unless a `context` distinguishes them.

Machine-checkable form:

1. If lesson A declares `conflicts-with` with a ledger ID that belongs to lesson B, and both are `active`, and their contexts do not distinguish each other (section 3.5), the lint fails.
2. The fix is one of: add distinguishing `context` fields to both lessons; mark one lesson `status: contested` with an `issue` link to a discussion; or mark one `superseded` with `by`.
3. A `contested` lesson without a valid `issue` link fails the lint.
   A `superseded` lesson without `by` fails the lint.

Authors declare conflicts when they notice them.
Reviewers check the rule by reading, and the review checklist in the PR template asks the question.
The lint cannot detect conflicts that nobody declared; the rule is therefore also a review duty.

## 7. Risks

### 7.1 Block markup

````markdown
```{warning} Venue contract lacks a cancellation clause
:class: hb-risk hb-likelihood-low hb-impact-high
risk | likelihood: low | impact: high | mitigation: Negotiate cancellation and relocation terms before signing and keep one backup venue shortlisted | owner-role: treasurer | playbook: venue-loss

If the venue cancels late, the team carries the cost of rebooking.
```
````

### 7.2 Fields

| Key | Required | Value |
|---|---|---|
| `likelihood` | yes | `low`, `medium` or `high` |
| `impact` | yes | `low`, `medium` or `high` |
| `mitigation` | yes | One sentence, at most 300 characters |
| `owner-role` | no | A role name, never a person |
| `playbook` | no | The `id` of an entry with `kind: playbook` in [chapter-list.yml](chapter-list.yml) |

Classes: `hb-risk`, `hb-likelihood-<likelihood>`, `hb-impact-<impact>`.
Titles are unique within one page.
The risk's ID is `<page-id>#risk-<slug of title>`, where the slug is the lowercase title with non-alphanumeric runs replaced by single hyphens.

Score: likelihood and impact map to 1 (low), 2 (medium), 3 (high); the score is their product (1 to 9).

### 7.3 The Risks section

Section 7 of every chapter contains either at least one risk block or exactly this sentence form:

```text
No chapter-specific risks recorded. Rationale: <one sentence>.
```

Chapter advice and risk advice never duplicate: each chapter carries its own risks, and Part 3 holds the method, the cross-cutting risks and the incident playbooks only.

## 8. Generated pages

The generator reads the whole `docs/` tree and writes these pages (kind `generated` in the chapter list).
A CI step regenerates them and runs `git diff --exit-code`; any difference fails the build (drift check).

Every generated page starts, after its minimal front matter, with the line:

```text
<!-- generated: do not edit; run the generator -->
```

Ordering "by chapter" always means the order of entries in [chapter-list.yml](chapter-list.yml), then document order within a page.

### 8.1 Lesson index (`lesson-index`)

One table per chapter that has lessons.
Columns: Title (the computed title), Scope, Confidence, Status, Ledger, Sources.
Rows are in rank order: general first, then recent, mid and old, each by year descending, then confidence, then first ledger ID.

### 8.2 Risk register (`risk-register`)

One table over all risk blocks.
Columns: Risk (linked to its section), Page, Likelihood, Impact, Score, Mitigation, Owner role, Playbook (linked).
Sorted by score descending, then page, then title.

### 8.3 Thin registry (`thin-registry`)

One table over all thin blocks.
Columns: Title (linked), Page, Kind, Area, Needs, Who might know, Issue, Since.
Sorted by page, then document order.

### 8.4 Decision register (`decision-register`)

One table over all decision items (section 1.4).
Columns: Page, Level, Decision (the bold span), Decide by.
Sorted by page, then document order.
Teams use it as a checklist when they fill the Tailoring Record.

### 8.5 Coverage map (`coverage-map`)

Two tables.
The first has one row for every entry that is not `generated`: id, status, maturity (if written), thin blocks by kind, lessons by scope, risk blocks.
The second has one row for each of the ten `area` values: the number of thin markers carrying that area.
A row with zero markers is shown, so a missing marker is visible.

## 9. Lint rule catalog

Each rule has a stable code so failures can be asserted in tests.
"Page" means a file listed in the chapter list with `status: written`.

| Code | Rule |
|---|---|
| B01 | Every managed block has a field line that parses (section 2.2). |
| B02 | No unknown, duplicate or empty key; the first segment matches the class-implied kind. |
| B03 | The directive matches the kind: `note` for lessons, `warning` for thin and risk. |
| B04 | The only option is `:class:`; its tokens match the computed set. |
| B05 | The block is in an allowed page kind and section (section 2.3). |
| B06 | Managed blocks use backtick fences, not colon fences. |
| L01 | Required fields present per scope; forbidden fields absent (section 3.2). |
| L02 | `year` is not greater than `as-of-year`. |
| L03 | All `source` IDs exist in the source manifest; all `ledger` IDs exist in the ledger. |
| L04 | For a specific lesson, every cited ledger row has the same year, place and org as the lesson, `source` equals the union of those rows' source IDs, and `confidence` equals the weakest confidence among those rows. |
| L05 | The title and the class set equal the computed values (section 3.3). |
| L06 | Case notes and Principles are in the required order (section 3.4). |
| L07 | `contested` requires a valid `issue`; `superseded` requires `by`; neither field appears otherwise. |
| L08 | General lessons satisfy the promotion rule (section 5). |
| L09 | The contradiction rule (section 6). |
| L10 | Ledger agreement, both directions. (a) Every ledger ID cited in a lesson's `ledger` field exists and its row has `disposition: placed: <this page id>#<any valid section slug>`. (b) For every ledger row with `placed: <page id>#<slug>` where that page is written, the token `L-nnnn` appears in that section. See [ledger schema](ledger-schema.md). |
| T01 | A thin block has `kind`, `needs` and `who-might-know`, with allowed values. |
| T02 | Section 8 holds at least one thin block or the exact "None known as of" sentence; a stub holds at least one thin block. |
| R01 | A risk block has valid `likelihood`, `impact` and `mitigation`. |
| R02 | `playbook`, when present, resolves to an entry with `kind: playbook`. |
| R03 | Section 7 holds at least one risk block or the exact "No chapter-specific risks recorded." sentence. |
| R04 | Risk titles are unique within a page. |
| N01 | Every top-level list item in section 3 carries exactly one level badge. |
| N02 | A MUST resolves to a register row, with matching as-of date and an allowed status (section 1.2). |
| N03 | A DEFAULT cites at least two ledger IDs from at least two distinct conferences. |
| N04 | Badges appear only where section 1.3 allows. |

Rule L10 runs against the ledger files described in [ledger-schema.md](ledger-schema.md).
Until a page is written, only the validity of the `placed` target (existing page id, valid slug) is checked for rows pointing at it.
