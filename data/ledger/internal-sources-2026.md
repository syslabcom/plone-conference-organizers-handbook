# Maastricht 2026 internal sources

> **Superseded IDs.** The INT-01…INT-12 identifiers below are superseded by manifest IDs S098…S109 (mapping: INT-01=S098, INT-02=S099, INT-03=S100, INT-04=S101, INT-05=S102, INT-06=S103, INT-07=S104, INT-08=S105, INT-09=S106, INT-10=S107, INT-11=S108, INT-12=S109). The D7-screened copies live in `data/sources/internal-2026/`; the ledger cites the S-IDs. This file is kept as provenance documentation; the "Contract extension for T5" section below is obsolete.

This register identifies the organizing records cited by the T7e ledger.
Paths are relative to the `syslabcom/ploneconference` organizing repository, except the explicitly identified GitHub issue.
These are provenance pointers, not permission to republish the underlying records.
Several sources contain personal or financial data and require D7 review before any further extraction.
No underlying source, attachment, dataset, or journal is copied here.

## Source register

Dates are the stated document dates where available; otherwise they identify inspection, not an inferred creation date.

| Source ID | Title | Repository path or remote record | Date | Description |
|---|---|---|---|---|
| INT-01 | Plone Conference 2026 facts and lessons for the handbook | `aftermath/documentation/2026-facts-for-handbook.md` | 2026-11-02, debrief recorded | Fifteen organizer facts with chapter targets, claimed scope, and verification gaps. |
| INT-02 | GitHub issues and project board collaboration review | `aftermath/documentation/github-collaboration-review.md` | 2026-11-02, analysis | Retrospective issue and board evidence with lessons L1–L4 and failure clusters. |
| INT-03 | Last-phase plan | `planning/last-phase-plan.md` | 2026-08-13, written; 2026-09-14, condensed | Final operational checklist, staged freezes, rehearsal gate, and no-response grant outcome. |
| INT-04 | On-site roles | `planning/roles/README.md` | 2026-08-13, written | Role narrative method, handoffs, helper shifts, and responsibility concentration risks. |
| INT-05 | Making contact: operator cheat sheet | `planning/marketing/MAKING_CONTACT.md` | 2026-11-02, inspected; authoring date unstated | Permission-first outreach process and authoritative tracker pattern. |
| INT-06 | Euregio contact kit | `planning/marketing/kit/README.md` | 2026-11-02, inspected; authoring date unstated | Modular contact preparation and limits on introductions, forwarding, and audience access. |
| INT-07 | Conference accounting overview | `aftermath/ploneconf-accounting/README.md` | 2026-11-02, inspected; authoring date unstated | Living-budget and shadow-ledger architecture, without financial records. |
| INT-08 | Conference accounting operator runbook | `aftermath/ploneconf-accounting/docs/operator-runbook.md` | 2026-11-02, inspected; authoring date unstated | Import cycle, manual boundaries, reconciliation, and committed-spend overlay safeguards. |
| INT-09 | Foundation requirements register | `aftermath/documentation/foundation-requirements-register.md` | 2026-11-02, register as-of | Existing R34–R37 confirmation candidates, retained as pointers rather than duplicated requirements. |
| INT-10 | Email campaigns | `communications/email/README.md` | 2026-11-02, inspected; authoring date unstated | MJML source and generated alternatives, dry-run testing, and environment-based credentials. |
| INT-11 | Attendance forecast implementation | `planning/sales-data/forecast.py` | 2026-08-30, embedded configuration date; inspected 2026-11-02 | Model structure and adaptation boundary only; script was read without execution or ticket-data access. |
| INT-12 | Global South grant application discussion | No local file; `syslabcom/ploneconference` issue 87: https://github.com/syslabcom/ploneconference/issues/87 | 2026-07-02, revised application; 2026-09-10, no-reply follow-up; inspected 2026-11-02 | Application argument structure, selection proposal, attachment pointer, and response trail; all concrete financial and personal content excluded. |

INT-12's revised application is at https://github.com/syslabcom/ploneconference/issues/87#issuecomment-4864540995.
The issue contains an application attachment pointer; the attachment was not downloaded or republished.
The final outcome available in INT-03 is that the grant was discarded after no response, rather than evidence of an award or formal rejection.

## Contract extension for T5

The ledger schema's LD06 and the configured source pattern accept only `S###` IDs that exist in the source manifest.
This extraction deliberately adds `INT-01` through `INT-12` without changing that manifest or the specification.
T5 needs an internal-source pattern, `^INT-[0-9]{2}$`, and resolution against this register, alongside the existing `^S[0-9]{3}$` manifest resolution.
Apply the same source-resolution extension to downstream lesson validation, source coverage, and bibliography generation.
The local self-check allows this explicit extension; it does not claim an unmodified G6/LD06 pass.

## Scope and confidence handling

The ledger retains `general` where the source offers a transferable principle or operating method, and `specific` for the dated implementation or retrospective finding.
General ledger scope records the source's claim; it does not establish the independent-conference promotion threshold or justify a DEFAULT or MUST badge.
No normative requirement is created by this harvest.

The facts file has no uniform confidence field on every fact.
Firsthand debrief experience and primary operating documents map to `observed`.
The explicitly reported university-tax claim stays `reported`; retrospective summaries in INT-02 also use `reported`.
Claims explicitly awaiting verification map conservatively to `hearsay` when the unresolved proposition is retained: the attendance trend, comparative attendance tactics, platform tariff, and speaker ratio.
The speculative streaming substitution claim also uses `hearsay` because no measured effect is supplied.
Decision framing can remain `observed` while stating that its underlying tax rule or numerical assumption is unverified.
This avoids converting an observation about a planning problem into verified tax advice or a verified attendance statistic.

F2's unresolved tax candidates remain R35/R36 in INT-09.
F12's duration and streaming candidate remains R34 there; the ledger adds only a scheduling-process pointer.
R37 retains the separate seed-finance question; this harvest creates no duplicate requirements-register entries.

## Sanitization boundary

No ticket exports, attendee or speaker lists, outreach target records, financial journals, bank exports, or private design documents were opened for this extraction.
No personal names, contact details, individual allocations, sponsor arrangements, private amounts, raw ticket totals, or concrete grant economics appear in the ledger.
The approximate community scale is a generalized, explicitly unverified planning hypothesis; the speaker ratio is reduced to a qualitative large-minority description.
The debrief's unverified platform rate is withheld pending a dated public tariff source.
Issue references, document dates, freeze dates, and task timing are provenance and process evidence, not private financial figures.
All rows are paraphrases.

| S111 | Organizer corrections and additions to the 2026 case file, 2026-11-02 | `aftermath/documentation/2026-11-02-case-file-corrections.md` | Recorded from the organizer review session; landed in the case file and ledger rows L-5069 to L-5076, with corrections to L-5043 and L-5017. | 2026-11-02 |
