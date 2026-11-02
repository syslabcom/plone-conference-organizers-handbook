<!-- Internal source copy (INT-01 in internal-sources-2026.md): aftermath/documentation/2026-facts-for-handbook.md; D7-screened 2026-11-02.; redactions: 1 -->

# Plone Conference 2026 — facts and lessons for the handbook

Recorded 2 November 2026 from the organisers' debrief (Alexander Pilz). Each fact
carries: the statement, where the evidence lives in this repository, the handbook
chapter it targets, its lesson scope per the handbook mechanics (general = timeless
principle; specific = dated case note with confidence level), and what still needs
verification before publication. These rows are seed content for plan tasks T7e
(ledger harvest) and T12 (2026 case file).

## Finance, tax and pricing

**F1 — Cross-border VAT was a top-level challenge.**
Organising in Maastricht (NL) while syslab/Cosent is a German-tax company created
real VAT complexity (Dutch BTW on tickets, refund questions from buyers — issue
#65 had to publish Dutch-VAT refund instructions mid-campaign).
Evidence: `aftermath/ploneconf-accounting/` (BTW rubriek report `bin/vat`, VAT
clearance patterns in the runbook); issue #65.
Target: Finance chapter + Contracts/legal; NL and DE jurisdiction annexes.
Scope: general lesson ("VAT regime follows the event's place of supply — resolve
your regime before pricing, not during sales") + specific 2026 case notes.
Verify: the exact place-of-supply rule and refund mechanics with the accountant
before publishing as guidance.

**F2 — Who sells the ticket changes the price participants pay.**
A company organiser must charge VAT; a university organiser sometimes does not
(reported, not verified); tickets sold by the US Plone Foundation carry no EU VAT.
For participants who cannot reclaim VAT through their employer this is a massive
real price difference.
Target: Finance chapter ("Decisions you must make": who is the financial agent).
Scope: general decision framing; the university claim is **reported** and must be
verified per jurisdiction before it becomes advice (T4 register candidate).
Verify: university/VAT claim; current Foundation ticketing practice.

**F3 — Global south tickets matter and need dedicated funding.**
2026 ran global-south pricing (issue #85, closed 29 July 2026) and pursued grant
funding for it.
Target: Ticketing chapter + Accessibility and inclusion chapter.
Scope: general principle (a global community prices for it) + specific 2026 case
note.

**F4 — The EuroPython grant argumentation is reusable.**
The argumentation used toward the EuroPython Foundation for financing global
south tickets should be published as a template (issue #87).
Evidence: locate the application text during T7e (not yet filed in this repo —
check mail/issue #87 attachments).
Target: Finance chapter templates (appendix).
Scope: specific 2026, reusable as a template with the argumentation generalised.
Verify: dig up the actual application; outcome (granted or not) must be recorded.

**F5 — Funding work is essential and can go wrong.**
Actively look for grants — but the Python Software Verband request (issue #83,
[redacted: D7 amount], filed 23 June 2026 as replacement for the annual Plone Tagung grant)
never recorded a response. Funding pipelines are uncertain; never budget a grant
as income before it is confirmed.
Target: Finance chapter; risk register (funding risk).
Scope: general principle + specific 2026 case notes.

**F6 — Late ticket purchases are a community pattern and they panic organisers.**
The Plone community buys late; cash-flow planning must expect it, and the
organisers' nerves need managing with data (see F14).
Target: Finance chapter (cash-flow); incident playbook "low ticket sales".
Scope: general (observed across multiple years — promote after ≥3-conference
evidence; the Tokyo 2018 early-sales plea in the bibliography is corroboration).

**F7 — Honest community size: ~100, tendency shrinking.**
Reality check for planning: recent in-person Plone conferences draw around 100
Plone people, tendency shrinking; previous conferences padded attendance with
local stunts — joining PyCon Finland (2025), heavily reduced local tickets
(Eibar 2023). 2026's own local-activation plans (issues #14 Maastricht
University, #66 RWTH) were never executed.
Target: Part 1 "Defining success" (attendance planning honesty); conference data
table in Part 5 (report real attendee composition).
Scope: general planning principle + specific data points (verify per-year numbers
against the data table sources).

**F8 — The budget setup is reusable: Guido's hledger system.**
`aftermath/ploneconf-accounting/` is a complete plain-text accounting setup:
living budget as periodic transactions converging on actuals
(`hledger balance --budget`), shadow double-entry ledger independent of the
parent company's SnelStart, idempotent CSV imports for ti.to and Stripe with
preprocessors, manual-entry patterns (invoiced sponsors, grants, VAT clearance,
refunds, contract commitment recognition), canned reports (`pnl`, `pnl-budget`,
`balance`, `vat` for the accountant's BTW rubrieken), a committed-spend overlay
so P&L includes contracted-but-unpaid venue obligations, smoke tests, and a
two-workstation git workflow with an operator runbook.
Caveats for reuse: the authoritative design doc lives in Guido's private
org-roam (outside this repo — must be rewritten for public consumption); the
bank-import step is agent-assisted, not fully mechanical; rules are specific to
ti.to + Stripe + ABN AMRO + Dutch BTW and need adaptation per organiser.
Target: Finance chapter template (T13: publish a sanitised, generic version with
the runbook as appendix; D7 sanitisation gate applies to the real journals).
Scope: general pattern ("plain-text accounting with a budget file and import
rules") + specific 2026 implementation.
Note: the shared budget was only closed as an issue on 10 September 2026 — eleven
days before the conference. The tooling worked; it was stood up far too late
(github-collaboration-review L4).

## Tickets and platform

**F9 — The ticket platform fee is a real line item.**
Tito takes 2.9% (as of 2026 — dated fact, re-verify). Alternative worth
documenting: self-hosted pretix with invoice/bank-transfer payment only, viable
because attendees are nearly all community members.
Target: Ticketing chapter ("Decisions you must make": platform and payment mix);
conference data table records the fee actually paid.
Scope: general decision framing + dated specific fee figure.

## Expectations (new chapter: Community and speaker expectations)

**F10 — Expectancies must be known from the start.**
The community and speakers carry implicit expectations that were never written
down and that blindside first-time organisers. This becomes a dedicated Part 1
chapter (the handbook's origin problem in miniature). Initial content:
- **Trainer hotel rooms are paid by the conference and should be on location or
  close by.** Speaker/trainer compensation is not regulated; organisers pay
  regardless of training length — the user names this the **biggest financial
  risk** of the conference. (The Bucharest 2015 Foundation minutes in the
  bibliography show the included-training model and trainer compensation already
  occupied the Foundation in 2015.)
- **Nobody expects a party** — there is no entitlement — but it is an important
  community element (2026: Thursday at Muziekgieterij, Friday deliberately empty).
- **Speakers expect a reduced ticket, and around 40% of participants are
  speakers** — a structural discount pressure on ticket revenue that pricing
  models must include from day one.
Target: new Part 1 chapter; Finance chapter (pricing model inputs); risk register.
Scope: general expectations list + specific 2026 ratios (40% — verify against
final ticket data in `planning/sales-data/final-tito.xlsx`).

## Programme, recording and streaming

**F11 — Recording talks is important and is real work.**
Effort and value both high; plan it as its own workstream with an owner (2026
evidence: A/V recording MVP planning on the board; issue #10/#28 stayed open even
though recording happened).
Target: AV, recording and internet chapter.
Scope: general.

**F12 — The Plone Foundation needs at least a 1-hour slot for the annual
meeting and report — 25 minutes is not enough — and the meeting should be
streamed** so absent members can follow.
Target: Scheduling chapter (MUST-class input; confirm with the Foundation → T4
register).
Scope: general (verify current Foundation requirement).

**F13 — PeerTube worked well and streaming has a real tradeoff.**
Good 2026 experience with PeerTube; it allows externals to join live, as did the
Corona-era streams. But streaming may keep some people from coming in person —
needs careful, explicit consideration per edition.
Target: AV chapter (PeerTube setup notes) + Hybrid/online chapter (the tradeoff
framed as a decision, not a default).
Scope: general tradeoff + specific 2026 tooling case note.

## Data and prediction

**F14 — Ticket purchase prediction research must be reusable.**
The 2026 research into predicting ticket purchases (against the late-buying
pattern, F6) should be published so future organisers can rerun it with their own
numbers.
Evidence: locate the model/data during T7e (candidates: `planning/sales-data/`,
`FINANCE/ticket-pricing/`); final actuals are `planning/sales-data/final-tito.xlsx`
(117 tickets, 5 party-only).
Target: Part 5 / appendix template + Finance chapter case note.
Scope: general method + specific 2026 dataset.

## Cross-cutting

**F15 — Issues + project board are a meaningful collaboration method for a
community conference** — with three preconditions (close-as-you-go hygiene, one
board holding all work, MUST items as checklist gates). Full analysis:
`github-collaboration-review.md`.
Target: Part 1 Team and governance; Part 4 Update process.
