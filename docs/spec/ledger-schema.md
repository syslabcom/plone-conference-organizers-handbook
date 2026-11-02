# Lessons ledger schema

The lessons ledger is the evidence layer between the sources and the chapters.
Every extraction from every source becomes one ledger row.
Every row ends up in exactly one of two places: placed in a chapter, or dropped with a reason.
Nothing is left unplaced (gate G7).

The ledger is the answer to the origin problem of this handbook: previous conferences passed on little, and much was expected but never written down.
A row that exists, with a disposition, cannot be silently lost.

Related files:
[README](README.md) · [conventions](conventions.md) · [chapter template](chapter-template.md) · [config defaults](handbook-config.yml) · [chapter list](chapter-list.yml)

## 1. Files and layout

- Ledger files are YAML, matched by the config key `paths.ledger-glob` (default `data/ledger/*.yml`).
- One file per extraction group (tasks T7a to T7f).
- Each file has two top-level keys:

```yaml
group: 7b
rows:
  - ledger_id: L-2001
    ...
```

- `group` is `7a`, `7b`, `7c`, `7d`, `7e` or `7f`.
- `rows` is a list of mappings, in any order. The generated ledger page sorts them by `ledger_id`.
- Ledger IDs are allocated by group so parallel extractions never collide:

| Group | Source group | ID range |
|---|---|---|
| 7a | Seattle 2006 | `L-1000` to `L-1999` |
| 7b | Bristol 2010 and Arnhem 2012 | `L-2000` to `L-2999` |
| 7c | San Francisco 2011 wiki and Brazil 2013 | `L-3000` to `L-3999` |
| 7d | Foundation CFPs and policies, 2022 to 2026 recaps, 2024 survey | `L-4000` to `L-4999` |
| 7e | The 2026 repository harvest, through the sanitization gate | `L-5000` to `L-5999` |
| 7f | 2026 attendee survey extraction | `L-6000` to `L-6999` |

## 2. Row schema

All keys are snake_case.
All keys below are required unless marked optional.

| Key | Type | Rule |
|---|---|---|
| `ledger_id` | string | Matches `ledger-id-pattern` (default `^L-[0-9]{4}$`). Unique across all ledger files. Inside the range for the file's group. |
| `topic` | string | The `id` of an entry in [chapter-list.yml](chapter-list.yml) whose kind is not `generated`. It names the subject the row is about. |
| `scope` | enum | `general` or `specific`. `general` means the source states the point as holding beyond its own conference. `specific` means it describes one conference. |
| `year` | integer | The year of the evidence: the conference year, or the year of the document for a policy. Between 2000 and `as-of-year`. |
| `place` | string | The city of the conference, or `n/a` for a document that is not tied to a place. 1 to 40 characters. |
| `org` | string | The organizing body that ran the conference or published the document. 1 to 60 characters. An organization, never a person. |
| `source_id` | string | Matches `source-id-pattern` and exists in the source manifest (`paths.source-manifest`). Gate G6. |
| `text_kind` | enum | `quote` or `paraphrase`. |
| `quote_or_paraphrase` | string | The evidence itself. See section 3. |
| `confidence` | enum | `observed`, `reported` or `hearsay`. See section 4. |
| `status` | enum | `active`, `contested` or `superseded`. |
| `disposition` | string | Exactly one of the two forms in section 5. The gate G7 field. |
| `locator` | string | Optional. Where in the source: a section name, a page number or a heading. |
| `issue` | string | Required when `status: contested`; forbidden otherwise. `#<n>` or a full GitHub issue URL. |
| `by` | string | Required when `status: superseded`; forbidden otherwise. The `ledger_id` of the row that replaces this one. |

No other keys are allowed.

Example rows (illustrative; the text is not evidence):

```yaml
group: 7b
rows:
  - ledger_id: L-2003
    topic: volunteers-and-roles
    scope: specific
    year: 2012
    place: Arnhem
    org: Four Digits
    source_id: S042
    text_kind: paraphrase
    quote_or_paraphrase: The registration desk had one more volunteer than planned and no queue formed.
    confidence: observed
    status: active
    disposition: "placed: volunteers-and-roles#case-notes"
    locator: Registration section

  - ledger_id: L-2004
    topic: catering
    scope: specific
    year: 2012
    place: Arnhem
    org: Four Digits
    source_id: S042
    text_kind: paraphrase
    quote_or_paraphrase: Dietary requirements were collected at registration but never passed to the caterer.
    confidence: reported
    status: active
    disposition: "dropped: duplicate of L-3011, which states the same point with better evidence"
```

Quote each `disposition` value, because it contains a colon.

## 3. The evidence text

1. A `quote` is the source's own words, at most `max-quote-words` words (default 40), in the source's language.
   If the source is not in English, add the English meaning as a paraphrase row with the same `source_id`.
2. A `paraphrase` is one to three sentences in American English, at most 120 words, stating the point in your own words.
3. Prefer paraphrase. A quote is for wording that matters, for example a rule or a requirement.
4. The text states one point. A source passage with three points becomes three rows.
5. D7 applies: no personal data, no contact details, no raw amounts from private books, no Tito user data.
   A public price may appear only with an as-of date and the source, for example "as of 2026-09".
   The privacy lint (gate G8) runs over the ledger files.

## 4. Confidence

| Value | Meaning |
|---|---|
| `observed` | The source author took part and describes their own experience, or the source is a primary document (a policy, a contract term, a published call). |
| `reported` | The source passes on something it learned from others, or summarizes without direct involvement. |
| `hearsay` | Anecdote or claim that cannot be checked. It may be recorded, but it never supports a MUST or a DEFAULT badge. |

When two rows disagree, the row's `status` and the contradiction rule in [conventions](conventions.md), section 6, decide what the handbook says.

## 5. The disposition (gate G7)

**Every row must have a disposition.**
A missing, empty or placeholder disposition fails gate G7.
The ledger is incomplete until every row is `placed` or `dropped`.

There are exactly two forms.

### 5.1 Placed

```text
placed: <page-id>#<section-slug>
placed: <page-id>
```

- `<page-id>` is an `id` in [chapter-list.yml](chapter-list.yml) whose kind is not `generated`.
- For a page of kind `chapter` or `playbook` the `#<section-slug>` part is required and must be a valid slug for that kind ([chapter template](chapter-template.md), sections 2 and 6.2).
- For pages of kind `page`, `annex` and `appendix` the `#...` part must be omitted.
- A row with `scope: specific` that becomes a lesson is placed at `<chapter>#case-notes`.
  A row that is cited as evidence for a general lesson is placed at the same chapter, usually `<chapter>#principles-and-general-lessons` or `<chapter>#case-notes`.
- A row whose point is used in prose (for example in How-to) is placed at that section.

Grammar:

```text
^placed: [a-z][a-z0-9-]*(#[a-z][a-z0-9-]*)?$
```

### 5.2 Dropped

```text
dropped: <reason>
```

- The reason is a sentence of at least 15 characters.
- It must not be a placeholder such as `n/a`, `tbd`, `todo` or `none`.
- Typical reasons: duplicate of another row (name its ID); out of scope for the handbook; too specific to transfer; private or unsafe to publish (D7); unverifiable; superseded.

Grammar:

```text
^dropped: .{15,}$
```

### 5.3 Consistency with the chapters

Gate G7 and lint rule L10 ([conventions](conventions.md), section 9) tie ledger and chapters together in both directions:

1. **Row to page.**
   For every row with `placed: X#S` where page `X` has `status: written`, the token `L-nnnn` (the row's ID) appears inside section `S` of that page.
   For `placed: X` without an anchor, the token appears anywhere on the page.
   For rows pointing at a page that is still `planned`, only the validity of the target (existing page, valid slug) is checked.
2. **Page to row.**
   Every ledger ID cited in a lesson's `ledger` field exists, and that row has `placed:` pointing at the same page.
3. **Dropped rows** are never cited by a lesson.
4. **Specific lessons** cite only rows whose `year`, `place` and `org` equal the lesson's own, whose `source_id` set equals the lesson's `source` list, and whose weakest `confidence` equals the lesson's `confidence` (rule L04).
5. A general lesson with `basis: independent-conferences` cites rows from at least three distinct (year, place) pairs and at least two distinct `org` values (rule L08).

## 6. Validation rules

| Code | Rule |
|---|---|
| LD01 | Each file has `group` and `rows`; `group` is one of the six values; no other top-level key. |
| LD02 | Every row has all required keys and no unknown key. |
| LD03 | `ledger_id` matches the pattern, is unique across all files, and lies in the group's range. |
| LD04 | `topic` resolves to a non-generated entry of the chapter list. |
| LD05 | `scope`, `text_kind`, `confidence` and `status` are valid enum values; `year` is an integer within range. |
| LD06 | `source_id` matches the pattern and exists in the source manifest (gate G6). |
| LD07 | A `quote` has at most `max-quote-words` words; a `paraphrase` has at most 120 words; the text is non-empty. |
| LD08 | `issue` is present exactly when `status: contested`; `by` is present exactly when `status: superseded` and resolves to an existing row. |
| LD09 | `disposition` is present and matches section 5.1 or 5.2, with the target rules for placed rows (gate G7). |
| LD10 | Row-to-page and page-to-row consistency (section 5.3). |
| LD11 | The file passes the privacy lint (gate G8). |

Tasks T7a to T7f validate their output against this table before they finish.
Every source document in a group must be cited by at least one row of that group's file (coverage), as set out in the plan's verification list.
