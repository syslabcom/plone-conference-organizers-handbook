# Front matter schema

Every authored page starts with a YAML front-matter block between two lines of three hyphens.
The block carries the page's ownership, freshness, maturity, applicability and metadata.
The contract test (gate G4) and the scheduled freshness workflow (gate G10) read it.

Related files:
[README](README.md) · [chapter template](chapter-template.md) · [conventions](conventions.md) · [config defaults](handbook-config.yml) · [chapter list](chapter-list.yml)

## 1. Fields at a glance

| Field | Type | Required for | Short description |
|---|---|---|---|
| `steward` | string | all kinds except `generated` | Who is accountable for the page. |
| `deputy` | string | all kinds except `generated` | Who steps in for the steward. |
| `review-by` | date | all kinds except `generated` | The date by which the page must be reviewed again. |
| `maturity` | enum | all kinds except `generated` | How far the page has come. |
| `applies-to` | list of strings | all kinds except `generated` | The context dimensions the page fits. |
| `diataxis` | enum | all kinds | The page type. |
| `myst` | mapping | all kinds | Holds `html_meta` for search and sharing. |
| `jurisdiction` | string | `annex` pages under `annexes/jurisdictions/` only | The ISO country code the annex covers. |

No other keys are allowed.
In particular `orphan` is not allowed: every page is reachable from a table of contents.
Dates are written unquoted (`2027-11-01`).
A YAML parser may return a date object or a string; the lint accepts both.

## 2. Field reference

### 2.1 `steward`

The person or team accountable for the page's accuracy.

- Allowed values: `unassigned`, a GitHub user handle (`@name`), or a GitHub team (`@org/team`).
- Handle pattern: `^@[A-Za-z0-9][A-Za-z0-9-]{0,38}(/[A-Za-z0-9._-]+)?$`.
- `unassigned` is allowed for `stub` and `draft` pages.
  Stewardship is a proposal until the community accepts it (decision D8).
- `reviewed` and `proven` pages require a named steward.
- Example: `steward: "@plone/conference-marketing"`.
  Quote values that start with `@`, because YAML treats a bare `@` as reserved.

### 2.2 `deputy`

The second accountable name, so a page is never one person away from orphaned.

- Same allowed values as `steward`.
- Must differ from `steward` unless both are `unassigned`.
- Example: `deputy: "@exampleuser"`.

### 2.3 `review-by`

The date by which someone must have re-read the page and either confirmed or updated it.

- Format: ISO date, `YYYY-MM-DD`.
- It must be a valid date and not later than the lint's as-of date plus `max-review-months` (24 by default).
- Pages whose facts age fast have a shorter limit: the ids and kinds listed under `fast-aging` in [the config](handbook-config.yml) allow at most `fast-aging.max-months` (12 by default).
- A date in the past does not fail the pull-request lint; it triggers the scheduled workflow, which opens one issue per overdue page (gate G10).
- Updating `review-by` is the act of re-confirming the page. The change appears in the diff and the reviewer sees it.
- Example: `review-by: 2027-11-01`.

### 2.4 `maturity`

How far the page has come, judged by the evidence it carries.

| Value | Meaning |
|---|---|
| `stub` | A skeleton with at least one thin marker. |
| `draft` | All sections have real content and at least one source. |
| `reviewed` | A reviewer other than the author checked it. At least two distinct sources and a named steward. |
| `proven` | An organizing team used it in a real conference. At least three distinct sources. |

The exact structural and evidence minimums are in [the chapter template](chapter-template.md), section 4.
The coverage map reads this field.
Example: `maturity: draft`.

### 2.5 `applies-to`

The context dimensions the page fits, as a YAML list of strings.
It must equal, as a set, the tokens in the page's "Applies when" section.

- Each item is one of:
  - `all`: applies to every conference. It must be the only item.
  - `<dimension>`: applies to all values; the content varies by this dimension.
  - `<dimension>=<value>[,<value>...]`: applies only to those values.
- Dimensions and their values are defined in [conventions](conventions.md), section 3.5: `size`, `jurisdiction`, `organizer`, `budget`, `venue`, `format`, `language`.
- Items are unique. Values within an item are unique.
- Quote every item that contains a comma, because YAML flow lists split on commas.

Examples:

```yaml
applies-to: [all]
applies-to: ["size=medium,large", "format=in-person"]
applies-to: [jurisdiction, budget=financial-agent]
```

### 2.6 `diataxis`

The page type, in the Diataxis sense, plus two additions.

| Value | Use |
|---|---|
| `tutorial` | Learning by doing, for example the Part 0 "Use" walkthrough. |
| `how-to` | A task-oriented procedure, for example an incident playbook. |
| `reference` | Lookup information, for example the glossary and generated registers. |
| `explanation` | Understanding-oriented text, for example the problem history. |
| `experience-report` | Accounts of what happened at specific conferences. |
| `mixed` | Several types on one page. Every `chapter` page uses it, because each section of the template has its own type. |

Fixed assignments by page kind (the lint enforces them):

| Page kind | Required `diataxis` |
|---|---|
| `chapter` | `mixed` |
| `playbook` | `how-to` |
| `generated` | `reference` |
| `page`, `annex`, `appendix` | any value above |

### 2.7 `myst`

A mapping that MyST turns into HTML meta tags.
It has exactly one key, `html_meta`, whose entries are:

| Key | Required | Rule |
|---|---|---|
| `"description lang=en"` | yes | One line, 50 to 160 characters, a plain sentence. No temporal words without a date. |
| `"keywords"` | yes | Comma-separated, at least three items, and the first item is `Plone`. |

Quote the keys, because they contain spaces.
No other `html_meta` keys are required. `sphinxext.opengraph` derives sharing tags from the description.

Example:

```yaml
myst:
  html_meta:
    "description lang=en": "How to decide who sells tickets and how VAT affects the price a participant pays."
    "keywords": "Plone, Plone Conference, ticketing, VAT, pricing"
```

### 2.8 `jurisdiction`

Only for annex pages whose `path` is under `docs/annexes/jurisdictions/`.

- Value: an ISO 3166-1 alpha-2 code in uppercase, for example `NL`.
- It is forbidden elsewhere.
- Example: `jurisdiction: NL`.

## 3. Complete examples

A written chapter:

```yaml
---
steward: "@plone/conference-marketing"
deputy: "@exampleuser"
review-by: 2027-11-01
maturity: draft
applies-to: ["size=medium,large"]
diataxis: mixed
myst:
  html_meta:
    "description lang=en": "How to plan sponsor packages, set expectations and keep sponsor promises."
    "keywords": "Plone, Plone Conference, sponsors, sponsorship"
---
```

A jurisdiction annex stub:

```yaml
---
steward: unassigned
deputy: unassigned
review-by: 2027-06-30
maturity: stub
applies-to: [jurisdiction=NL]
diataxis: reference
myst:
  html_meta:
    "description lang=en": "General notes on Dutch tax and legal points for a Plone Conference. Not legal advice."
    "keywords": "Plone, Plone Conference, Netherlands, VAT, annex"
jurisdiction: NL
---
```

A generated page (minimal block):

```yaml
---
diataxis: reference
myst:
  html_meta:
    "description lang=en": "All thin markers in the handbook, collected so contributors can see where help is needed."
    "keywords": "Plone, Plone Conference, thin content, contributing"
---
```

## 4. Validation rules

Each rule has a code for use in tests.

| Code | Rule |
|---|---|
| F01 | The block exists, is valid YAML, and contains no key outside section 1. |
| F02 | All fields required for the page kind are present; no field forbidden for that kind is present. |
| F03 | `steward` and `deputy` match the allowed values, differ unless both `unassigned`, and are named for `reviewed` and `proven`. |
| F04 | `review-by` is a valid date within the allowed horizon (section 2.3). |
| F05 | `maturity` is one of the four values. |
| F06 | `applies-to` items are valid tokens, `all` stands alone, and the set equals the "Applies when" tokens on `chapter` pages. |
| F07 | `diataxis` is allowed and matches the fixed assignment for the page kind. |
| F08 | `myst.html_meta` has a valid description and keywords. |
| F09 | `jurisdiction` is present exactly on jurisdiction annexes and is a valid code. |

## 5. Scheduled freshness (gate G10)

A scheduled workflow lists every written page whose `review-by` is before today and opens one issue per page, naming the steward and the deputy.
If a page already has an open freshness issue, the workflow adds no second one.
Closing the issue requires a commit that moves `review-by` forward.
