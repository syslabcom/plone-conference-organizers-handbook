# GitHub issues and project board — 2026 collaboration review

Analysed 2 November 2026 from live data (`gh issue list --state all`, `gh project
item-list 37 --owner syslabcom`). Raw captures: `.omo/gh-analysis/`. This review
feeds the handbook plan (evidence base 5) and answers: does issues + project board
work as the collaboration method for a conference, what did we plan, what did we
actually do, and what do the never-completed issues teach.

## The numbers

- **110 issues** in `syslabcom/ploneconference`: **58 closed, 52 open** at analysis
  time — five weeks after the conference ended.
- **Project board 37** holds only **30 items** (21 Done, 6 In Progress, 2 Review,
  1 Comunicate) — i.e. 80 issues never made it onto the board, so the board was
  never the operational truth it was intended to be.
- No milestones were used at all (110/110 unmilestoned); labels were used
  inconsistently (Focused / Planning / Epic / Critical).

## Cluster A — done in reality, never closed (status hygiene)

The conference demonstrably happened: the party was booked and held, t-shirts and
badges were produced and ordered, A/V recorded talks, the sprint ran. Yet these
issues are still open: #5 printed agenda for goodie bags, #6 goodie bag, #7
conference party, #9 sprint organisation, #10 microphones/cameras, #28 session
recording plan, #56 party music thoughts, #75 t-shirt design, #89 Van der Valk
final numbers, #93 badges.

**Lesson L1.** In the final six weeks nobody maintains the tracker. The board
decays into a historical artefact exactly when it should be the coordination hub.
Any handbook process that relies on an issue board must include a close-as-you-go
rule and a weekly triage ritual, or accept that the board is a planning tool, not
an execution tool.

## Cluster B — genuinely dropped (the interesting failures)

- **#22 Check insurance requirements for the venue** — never done. Insurance is a
  MUST-class item; it survived ten months as an open planning issue and shipped
  unresolved.
- **#23 Coordinate venue accessibility** — never done. No accessibility
  documentation for the website was produced. (Handbook thin area confirmed by
  practice.)
- **#14 / #66 Reach out to Maastricht University / RWTH** — never done. Local
  audience activation — the tactic Eibar used with reduced-price local visitors —
  was planned and silently dropped.
- **#42, #48, #50, #51, #52 — the decision-maker research programme.** A
  "convince your boss" page (inspired by Scale Computing's conference page), a
  10-minute interview script, an interviewee list, an anonymous survey and a
  LinkedIn poll were specced in February 2026; the scripts were actually written
  (see issue comments) and then none of it was executed.
- **#17 Document planning in docToolchain** — the team's own "documentation for
  the next organiser, with templates" ambition, opened 24 October 2025, never
  started. The meta-lesson: the handbook you are reading about is the third
  attempt at this idea (Seattle 2006 wrote prose, SF 2011 used a wiki, 2026
  planned docToolchain) — tooling ambition beyond the team's daily habits is the
  failure mode. What actually got used was a plain folder of Markdown files.
- **#83 Request sponsorship grant from Python Software Verband** — a €1,000 grant
  request filed 23 June 2026 (as replacement for the annual Plone Tagung grant,
  since the German track merged into Maastricht because Uni Bonn could not offer
  date/place). No response ever recorded; the issue is still open. Funding
  uncertainty made visible.
- **#107 / PR #106 story engine** — an AI LinkedIn-content generator showcased at
  a marketing meeting; example output was PRed and never adopted into practice.

**Lesson L2.** The drops cluster in four places: legal/insurance, accessibility,
local audience development, and research ambitions beyond team capacity. The
handbook counters: insurance and accessibility become MUST items in the Contracts
and Accessibility chapters (checklist gates, not aspirations); local activation
and pre-conference research become explicit scope decisions with an owner and a
drop-by date recorded in the Tailoring Record.

## Cluster C — the Epic layer was abandoned

Nine epics (#29–#38, #41, #44) were created on 27 October 2025 to structure the
work (Core Planning, Venue, Website & Marketing, Program, Community, Tickets &
Sponsors, Roles, Merchandise, Party, Finance, Legal, Business Track). All nine are
open; real work happened in small "Focused" issues.

**Lesson L3.** A two-level hierarchy (epic → task) was one level too many for a
team of this size. One flat list with good titles and a weekly triage beats a
structure nobody maintains.

## Cluster D — timing facts the issues reveal

- **#19 Set up a shared conference budget** and **#21 Clarify sponsor invoicing**
  were both closed on **10 September 2026** — eleven days before the conference.
  *Correction 2026-11-02 (organizer): budgeting and accounting were in place
  earlier; the issues were simply closed late. The closure dates misled the
  first version of this review — closure dates are tracker hygiene, not work
  dates.*
- **#65 Dutch VAT refund instructions link** closed 17 June 2026 — the
  cross-border VAT problem surfaced in ticket sale support and had to be answered
  publicly.
- **#85 Ticket pricing Global south** closed 29 July 2026; **#87 check EuroPython
  application** closed 2 July 2026 — the global-south ticket and grant work
  happened, mid-campaign.

**Lesson L4.** Stand financial tooling up at the start of ticket sales (advice
the 2026 team followed — see the correction above), and reuse more of the
conference website tooling and of the content that recurs every edition;
dependency on external deployments was a factor for delays. (The 2026-11-02
organizer corrections also removed a website-defect case note from this lesson;
the general website-QA gate remains in the handbook's web chapter.)

## Verdict on issues + board as the collaboration method

Worth keeping — with discipline. It gave community helpers a visible queue (#12
interview task, #58 Upwork design help, #91 enlist supporters show outsiders
plugging in), it preserves rationale in comments (the #48/#51 research scripts
survive only because they live in issue comments), and it is the natural habitat
of a software community. But 2026 shows three preconditions: close-as-you-go
hygiene (Cluster A), one board that actually contains all work (Cluster D drift),
and MUST items tracked as checklist gates so insurance and accessibility cannot
silently drop (Cluster B). This verdict and these preconditions land in the
handbook's Part 1 (team and governance) and the Web chapter (QA gate).

## Handbook mapping

| Finding | Lands in |
|---|---|
| L1 close-as-you-go, weekly triage | Part 1 — Team and governance; Part 4 Update |
| L2 MUST gates for insurance/accessibility; drop-by dates | T4 requirements register; chapters Contracts, Accessibility; Tailoring Record |
| L3 flat list over epic hierarchy | Part 1 — Team and governance |
| L4 budget-at-start, website-QA gate | Finance chapter; Web chapter; T-minus checklist |
| #111 case note (speaker search, day-before discovery) | Web chapter Case notes `[specific · 2026 · Maastricht]` |
| #83 funding uncertainty case note | Finance chapter Case notes; Funding risk in risk register |
| #17 tooling-ambition meta-lesson | Part 0 honesty statement; Part 4 (keep the handbook plain Markdown) |
