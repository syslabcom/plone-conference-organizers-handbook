# Governance sketch

**Status: a proposal to the community (decision D8), not a decision.**
Nothing here binds anyone until the Plone Foundation, the Conference Committee and conference organizers accept it.
Until then every `steward` and `deputy` field may read `unassigned`, and the repository's incubating maintainers act as one interim team.

Related files:
[README](README.md) · [front matter](front-matter.md) · [conventions](conventions.md) · [config defaults](handbook-config.yml)

## 1. The idea

Maintaining the handbook becomes part of an organizer's duties, not an act of goodwill.
The outgoing team owes a handover (section 4).
The incoming team uses it to update the handbook (section 2).
Community members who guide conference organization across the years, for example the marketing team, carry stewardship (section 3).

## 2. The annual update ritual

The **incoming** team performs the update with the outgoing team.
Dates count from the last conference day (T+0) and are proposed.

| By | Step |
|---|---|
| T+60 days | The six handover deliverables arrive (section 4). |
| T+75 days | The post-mortem and the anonymized survey results are filed under `conferences/<year>-<city>/`. |
| T+90 days | Lessons arrive as pull requests: every ledger row has a disposition, every lesson cites a ledger ID, and the promotion rule applies ([conventions](conventions.md), section 5). |
| T+100 days | The outgoing team's Tailoring Record is filed as `conferences/<year>-<city>/tailoring.md`. Recurring deviations show where a DEFAULT should become an OPTION. |
| T+110 days | The requirements register is re-verified and every MUST badge is re-dated. |
| T+120 days | `as-of-year` is bumped, the generator runs, thin markers become "help wanted" issues, promotions are logged, and the CalVer tag `<year>.1` is cut. |

A scheduled workflow opens one issue per page past its `review-by` date all year ([front matter](front-matter.md), section 5).

## 3. Rotation, stewards and CODEOWNERS (proposal)

1. The incoming team leads the update. The outgoing team assists.
2. A lesson's author is never its only reviewer. For a lesson from year Y, one reviewer comes from an organizing body other than Y's.
3. A chapter's steward and deputy come from different organizations.
4. At each ritual a deputy may move up to steward, and the incoming team nominates a new deputy. Rotation prevents single-organizer capture.
5. Each chapter names a `steward` and `deputy` in its front matter. A `CODEOWNERS` file maps paths to GitHub teams, for example `/docs/workstreams/marketing/ @plone/conference-marketing`.
6. The Foundation holds repository admin. A bus-factor figure (distinct people who can merge) is reported at each annual release.

Version 1 runs on the interim team. After community buy-in, `CODEOWNERS` names at least three maintainers across at least two organizations. That gate does not apply to version 1.

## 4. The handover contract deliverables

The outgoing team owes the next team these six items by **T+60 days** (proposed deadline):

1. **Post-mortem**, on the Seattle 2006 skeleton.
2. **Financial summary**: final income and costs by category, the result, and the budget model. Generalized per D7.
3. **Anonymized survey data**: aggregates only.
4. **Asset and credential handover**: a list of accounts, domains and assets and their new holders. Credentials pass through a password manager or the Foundation, never the repository.
5. **Vendor contacts**: organization-level, handed over privately. The public handbook lists none.
6. **The "expected but never written down" list**: every implicit expectation the team ran into.

The contract also sets a **shadowing arrangement**: the incoming team follows the outgoing team's final months and the event. Bucharest 2027 is the first real shadow.

## 5. Open questions

1. Who accepts this model: the Foundation board, the Conference Committee, or both?
2. Is T+60 days realistic for volunteer teams?
3. Which team carries stewardship from version 1?
