<!-- Internal source copy (INT-09 in internal-sources-2026.md): aftermath/documentation/foundation-requirements-register.md; D7-screened 2026-11-02. -->

# Foundation Requirements Register (Level A)

Task T4 of `aftermath/documentation/organisers-handbook-plan.md`.
As of 2026-11-02.
Status: draft for the human gate; nothing here has been sent to the Plone Foundation.

## Purpose and how to read this register

Every MUST badge in the handbook cites one row of this register (plan section 5.1).
A row records what the Plone Foundation, or the Conference Committee acting for the Foundation, places on conference organizers, where that is written down, and whether it still stands today.

Most hard requirements come from the Foundation's calls for proposals (CFPs) to host the conference.
The CFPs read here date from 2015–2019 (the 2016–2019 editions, plus the 2020 edition issued in August 2019), so they are 7–11 years old.
That age is exactly why this re-verification pass exists.
No hosting CFP issued after the 2020 edition was located (one web search on 2026-11-02, plus the plone.org conference archive pages).
A requirement that cannot be re-verified against a current, standing Foundation document is still recorded, marked `unverifiable`, with the archived copy as the surviving source.

The Foundation itself has said that no consolidated requirements list exists.
The 2023 board minutes record the organizer's suggestion that "Plone Foundation should provide guidelines for future conferences", and the Board's published 2025 priorities include "Have a written list of requirements to organize Conferences/Sprints/...".
This register is a candidate for that list, which is one of the questions for the Foundation below.

### Status values

- `verified-current` — a live plone.org page fetched on 2026-11-02 that is a standing policy, resolution or Conference Committee page (not an edition-specific CFP) states the requirement today.
- `verified-changed` — live or official evidence shows the requirement changed or is not applied as written.
- `unverifiable` — only edition-specific CFPs state it; no current Foundation document restates it; the archived or still-live historical text is the surviving source.
- `unverified-pending-Foundation-ask` — a 2026 debrief candidate that no Foundation document addresses; it waits for the Foundation ask bundle.

### Source force and proposed badge

"Source force" records how strongly the source itself words the item: `required` (must, required elements, requirements), `conditional` (binding only when a condition applies, for example Foundation funding), `encouraged` (strongly encouraged or suggested design), or `guidance` (Committee planning schedule).
"Proposed badge" is this register's recommendation for the handbook (MUST, DEFAULT or OPTION).
Only rows that are `required` or `conditional` and `verified-current` are proposed as MUST without further confirmation.
Everything else needs the Foundation's answer before it can carry a MUST badge.

### Source paths

`BIB/` abbreviates `aftermath/documentation/references/bibliography/`.
All `BIB/` files are read-only archived copies fetched on 2026-11-02 (see `BIB/manifest.csv`).
Three sources have no local archived copy and are cited by live URL only: the 2020 CFP, the Plone Event Financial Policy resolution and the Board's 2025 priorities.
They should be added to the archive in a later fetch run (this task does not modify `references/`).

## Requirements table

| ID | Requirement | Source (local archive + live URL) | As of | Status | Status note | Source force | Proposed badge | Handbook target chapter |
|---|---|---|---|---|---|---|---|---|
| R01 | An event may only be called "Plone Conference <year>" or "International Plone Conference" if the Foundation approves it, and the Foundation selects its location. | `BIB/general-and-current-planning-resources/plone-event-naming-guidelines.html` — https://plone.org/foundation/about/materials/foundation-resolutions/conference-naming | 2026-11-02 | verified-current | Live resolution unchanged since its 1 November 2012 amendment. | required | MUST | Part 1 — Team and governance; Part 2 — Web, comms and brand |
| R02 | An event using "Plone" in its name must primarily feature Plone and must not present itself as Foundation-endorsed unless the Foundation explicitly endorsed it. | `BIB/general-and-current-planning-resources/plone-event-naming-guidelines.html` — https://plone.org/foundation/about/materials/foundation-resolutions/conference-naming | 2026-11-02 | verified-current | Live text matches the archived copy. | required | MUST | Part 2 — Web, comms and brand |
| R03 | Hosting proposals go to board@plone.org as PDF or ODF, the Board pre-qualifies them, Foundation members vote, and the Board bears ultimate responsibility for the award. | `BIB/2016-boston/2016-call-for-proposals-codified-requirements-and-recommende.html`, `BIB/2017-barcelona/2017-call-for-proposals.html`, `BIB/2018-tokyo/2018-call-for-proposals.html`, `BIB/2019-ferrara/2019-call-for-proposals-budget-cash-flow-team-affordability.html` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals; live only: https://plone.org/news-and-events/events/plone-conferences/online-2020/2020-call-for-proposals | 2026-11-02 | unverifiable | Stated in every CFP 2016–2020; no hosting CFP after 2020 located, so the current selection process is undocumented. | required | MUST pending confirmation | Part 1 — Team and governance; Part 2 — City selection |
| R04 | A hosting proposal must include a complete conference budget covering all costs and revenue. | `BIB/2016-boston/…`, `BIB/2017-barcelona/…`, `BIB/2018-tokyo/…`, `BIB/2019-ferrara/2019-call-for-proposals-budget-cash-flow-team-affordability.html` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals; live only: 2020 CFP URL as in R03 | 2026-11-02 | unverifiable | CFP-only "required element"; R05 carries the current, weaker planning-schedule equivalent. | required | MUST pending confirmation | Part 2 — Finance |
| R05 | The organizer develops and tracks a budget with sponsor income, ticket income and expenses, including a Plone Foundation line. | `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | Live Committee schedule, already updated for 2026; the "Plone Foundation" expense line is the current trace of R10. | guidance | DEFAULT | Part 2 — Finance |
| R06 | A hosting proposal must explain how the organizer will manage cash flow, because money must be committed before sponsorship and registration income arrives. | CFP set as in R04 (`BIB/2019-ferrara/2019-call-for-proposals-budget-cash-flow-team-affordability.html` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only; the risk itself is well evidenced (Seattle 2006 needed a USD 8,000 advance, see R37). | required | MUST pending confirmation | Part 2 — Finance; Part 3 — cash-flow crunch playbook |
| R07 | A hosting proposal must state explicitly whether the organizers ask the Foundation to be the financial agent for the event. | `BIB/2018-tokyo/2018-call-for-proposals.html`, `BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals; live only, no local archive: https://plone.org/foundation/about/materials/foundation-resolutions/plone-event-financial-policy | 2026-11-02 | verified-current | Live Plone Event Financial Policy resolution (Board approval 26 January 2017, effective the same day) states it verbatim; no amendment shown. | required | MUST | Part 1 — Legal entity and financial agent |
| R08 | If the Foundation acts as financial agent, it assumes the financial risk and grants use of its banking and PayPal accounts, accounting systems and Treasurer, but does not pay the organizers' extra work hours. | live only: https://plone.org/foundation/about/materials/foundation-resolutions/plone-event-financial-policy; also `BIB/2019-ferrara/2019-call-for-proposals-budget-cash-flow-team-affordability.html` | 2026-11-02 | verified-current | Policy text live; whether the offer is still extended in practice is not stated anywhere, and the 2025 priorities mention a "treasury transfer" — see Q6. | conditional | MUST (when agent) | Part 1 — Legal entity and financial agent; Part 2 — Finance |
| R09 | In exchange, the organizers send the Board regular updates, at least one Board member joins the planning, the Board has final authority on all financial decisions, and the Foundation receives any surplus. | live only: https://plone.org/foundation/about/materials/foundation-resolutions/plone-event-financial-policy; also `BIB/2018-tokyo/2018-call-for-proposals.html` | 2026-11-02 | verified-current | Policy text live and unchanged. | conditional | MUST (when agent) | Part 1 — Legal entity and financial agent |
| R10 | The Foundation collects a share of per-person registration revenue (15 %, not of sponsorship) after the conference, and the organizer budgets for it. | `BIB/2016-boston/…`, `BIB/2017-barcelona/…`, `BIB/2019-ferrara/…` (15 %), `BIB/2018-tokyo/2018-call-for-proposals.html` (20 %) — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals; `BIB/2023-eibar/foundation-board-minutes-with-the-organizer-s-conference-rep.html` — https://plone.org/foundation/meetings/minutes/2023/plone-foundation-board-minutes-november-2-2023 | 2026-11-02 | verified-changed | Rate moved 15 % → 20 % (2018) → 15 % (2019, 2020); the live 2023 minutes record the organizer "will do 10% donation"; no standing document states today's rate or form — see Q5. | required | MUST pending confirmation | Part 2 — Finance |
| R11 | A hosting proposal estimates the cost per attendee and keeps the conference affordable, with a target of USD 250–450 per person. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only; the dollar band dates from 2015–2019 and is not restated anywhere current. | required | DEFAULT | Part 2 — Ticketing and registration |
| R12 | Organizers must perform due diligence on local law to establish which types and limits of insurance coverage the event requires. | `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship; live only: https://plone.org/news-and-events/events/plone-conferences/online-2020/2020-call-for-proposals | 2026-11-02 | verified-current | Live sponsorship policy states it for Foundation-supported events; the 2020 CFP (first CFP with this clause) states it for conference hosts; whether proof is required is open — see Q9. | required | MUST | Part 2 — Contracts, legal and insurance |
| R13 | The conference adheres to the Plone Code of Conduct, publishes it on the website, and makes ticket buyers agree to abide by it. | CFP set as in R04 (`BIB/2019-ferrara/…`); `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | CFPs "expect adherence"; the live Committee schedule lists the code on the website and in the ticketing agreement. | required | MUST | Part 2 — Code of Conduct operations; Ticketing and registration |
| R14 | The website and ticketing include the attendee's agreement to be photographed. | `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | Live schedule lists it twice (website launch, ticketing); legal sufficiency under GDPR is a separate counsel question. | guidance | DEFAULT | Part 2 — Privacy and GDPR; Ticketing and registration |
| R15 | The published schedule includes the Plone Foundation annual member meeting, which is held once a year at the conference. | `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule; `BIB/general-and-current-planning-resources/board-and-member-meetings-archive.html` — https://plone.org/foundation/meetings | 2026-11-02 | verified-current | Both pages live; neither states a duration or streaming requirement — that is R34. | guidance | MUST (Foundation meeting coincides with conference) | Part 2 — Scheduling |
| R16 | The organizer plans to record as many sessions as possible, preferring fast turnaround, with live streaming optional. | CFP set as in R04 (`BIB/2016-boston/…` "recording and streaming"; `BIB/2018-tokyo/…`, `BIB/2019-ferrara/…` "recording (and, optionally, streaming)"); `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | Live schedule: "recording (optional: live streaming)"; streaming was softened from expected (2016–2017) to optional (2018 onward). | encouraged | DEFAULT | Part 2 — AV, recording and internet |
| R17 | The conference design includes pre-conference trainings (CFPs: 1–2 days). | CFP set as in R04 (`BIB/2019-ferrara/…`); `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | Live schedule keeps the call for trainers, trainer housing and the training survey; the day count is CFP-only. | encouraged | DEFAULT | Part 2 — Trainings |
| R18 | The conference design includes post-conference sprints (CFPs: 2–3 days, with an experienced sprint leader). | CFP set as in R04 (`BIB/2019-ferrara/…`); `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | Live schedule keeps a sprint venue and "sprint organization (September)"; the day count is CFP-only. | encouraged | DEFAULT | Part 2 — Sprints |
| R19 | The conference design includes three days of conference talks. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only "suggested design"; not restated in any current page. | encouraged | DEFAULT | Part 2 — Programme portfolio |
| R20 | The conference is held between mid-September and mid-November and avoids major religious and national holidays. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only; the live schedule only says the conference "is held in the fall", which is consistent but less specific. | required | DEFAULT pending confirmation | Part 1 — Master timeline; Part 2 — City selection |
| R21 | The venue must hold 200–500 people (250–500 in 2016–2017) in a plenary room, with breakout rooms for 2–3 tracks and informal gathering space. | CFP set as in R04 (`BIB/2016-boston/…`, `BIB/2017-barcelona/…` 250–500; `BIB/2018-tokyo/…`, `BIB/2019-ferrara/…` 200–500) | 2026-11-02 | unverifiable | CFP-only; the 2026 edition sold 117 tickets (`planning/sales-data/final-tito.xlsx`), so the floor no longer matches practice. | required | OPTION pending confirmation | Part 2 — Venue |
| R22 | The venue provides reliable wireless access for all attendees at once and appropriate audio-visual support. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only as a specification; the live schedule keeps "wifi" as a planning item without a capacity standard. | required | DEFAULT pending confirmation | Part 2 — AV, recording and internet; Venue |
| R23 | The venue is at most one hour from an international airport, with affordable transport so attendees need no car. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only. | required | DEFAULT pending confirmation | Part 2 — City selection; Hotels and local logistics |
| R24 | The conference provides snacks, coffee and lunch. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only as a requirement; the live schedule keeps "food & beverage service" as a planning item. | required | DEFAULT pending confirmation | Part 2 — Catering |
| R25 | The organizer provides invitation letters and visa-application support throughout the planning period. | `BIB/general-and-current-planning-resources/conference-planning-schedule.html` — https://plone.org/community/teams/conference/conference-planning-schedule | 2026-11-02 | verified-current | Live schedule item; the 2023 minutes add that Google Summer of Code student visas need starting before summer. | guidance | DEFAULT | Part 2 — Visas and travel |
| R26 | A hosting proposal names the key people, their history with the Plone community, and their event-organizing experience. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only. | required | MUST pending confirmation | Part 1 — Team and governance |
| R27 | A hosting proposal includes a conference marketing plan and a plan for engaging the community in the agenda. | CFP set as in R04 (`BIB/2019-ferrara/…` — https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals) | 2026-11-02 | unverifiable | CFP-only. | required | MUST pending confirmation | Part 2 — Marketing and outreach; CFP and selection |
| R28 | The organizer considers how to reduce the event's environmental footprint. | CFP set as in R04 (`BIB/2019-ferrara/…`); `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship; live only: https://plone.org/news-and-events/news/news-for-2025/plone-foundation-board-2025-priorities | 2026-11-02 | verified-current | Live sponsorship policy and 2025 priorities name lowering the carbon footprint as a Board priority; the CFP "green conference" list is encouragement only. | encouraged | OPTION | Part 2 — Sustainability |
| R29 | The organizing team works with the Conference Committee, which provides continuity between editions and is reached at conf@plone.org. | `BIB/general-and-current-planning-resources/conference-committee.html` — https://plone.org/community/teams/conference | 2026-11-02 | verified-current | Live page lists 2026 members; see the Conference Committee section. | guidance | DEFAULT | Part 1 — Team and governance; Handover contract |
| R30 | Any event that receives Foundation funding declares in all its communications "The <EventName> is funded by the Plone Foundation". | `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship | 2026-11-02 | verified-current | Live text unchanged; applies only to funded activities (for example a funded post-conference sprint). | conditional | MUST (when funded) | Part 2 — Sponsors; Web, comms and brand |
| R31 | Foundation funds may not buy alcohol for resale, and alcohol paid from them is only for consumption with meals. | `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship | 2026-11-02 | verified-current | Live text unchanged; conditional on Foundation funding. | conditional | MUST (when funded) | Part 2 — Social events and party; Finance |
| R32 | A funded event reports back via the Sponsorship Report Form and a plone.org news item before reimbursement. | `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship | 2026-11-02 | verified-current | Live text unchanged; reimbursement then runs through treasurer@plone.org. | conditional | MUST (when funded) | Part 2 — Sprints; Finance |
| R33 | Funding requests go through the plone.org form, at least one month ahead for community sprints and by December of the prior year for strategic sprints. | `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship | 2026-11-02 | verified-current | Live text unchanged; the strategic deadline is soft ("not an absolute deadline"). | conditional | MUST (when requesting funds) | Part 2 — Sprints; Finance |
| R34 | Does the Foundation require at least a one-hour, streamed slot for its annual member meeting and report, given that 25 minutes proved insufficient in 2026? | `aftermath/documentation/2026-facts-for-handbook.md` (F12); context: `BIB/general-and-current-planning-resources/board-and-member-meetings-archive.html` — https://plone.org/foundation/meetings | 2026-11-02 | unverified-pending-Foundation-ask | No Foundation page read states a duration or streaming rule; R15 only confirms the meeting coincides with the conference. | — | MUST candidate | Part 2 — Scheduling; AV, recording and internet |
| R35 | Can a university organizer sell tickets without charging VAT where a company organizer must charge it, and in which jurisdictions? | `aftermath/documentation/2026-facts-for-handbook.md` (F2, marked "reported, not verified") | 2026-11-02 | unverified-pending-Foundation-ask | No Foundation document read mentions VAT; this is jurisdiction law, so the Foundation can at most share experience — a tax adviser must confirm per country. | — | MUST candidate (jurisdiction annex) | Part 1 — Legal entity and financial agent; Part 2 — Finance |
| R36 | Does the Foundation still sell conference tickets itself (as a US entity, without EU VAT), and under which conditions? | `aftermath/documentation/2026-facts-for-handbook.md` (F2); live only: https://plone.org/foundation/about/materials/foundation-resolutions/plone-event-financial-policy | 2026-11-02 | unverified-pending-Foundation-ask | The financial-agent resolution grants use of Foundation accounts but says nothing about ticket sales or VAT. | — | MUST candidate | Part 1 — Legal entity and financial agent; Part 2 — Ticketing and registration |
| R37 | Does the Foundation still offer seed loans or advances against up-front costs, or act as financial agent, for the conference? | `BIB/2006-seattle/things-we-learned-about-running-a-plone-conference.html` — https://plone.org/news-and-events/events/plone-conferences/seattle-2006/evaluation/lessons-learned; `BIB/general-and-current-planning-resources/plone-event-and-sprint-sponsorship-policy.html` — https://plone.org/foundation/event-sponsorship; live only: https://plone.org/foundation/about/materials/foundation-resolutions/plone-event-financial-policy | 2026-11-02 | unverified-pending-Foundation-ask | Seattle 2006 received a USD 8,000 advance under a promissory note; the live sponsorship policy covers marketing events and sprints only and mentions no loan; the live financial policy offers the agent model but no loan. | — | MUST candidate | Part 1 — Legal entity and financial agent; Part 2 — Finance |

`CFP set as in R04` means the four archived CFPs (`BIB/2016-boston/2016-call-for-proposals-codified-requirements-and-recommende.html`, `BIB/2017-barcelona/2017-call-for-proposals.html`, `BIB/2018-tokyo/2018-call-for-proposals.html`, `BIB/2019-ferrara/2019-call-for-proposals-budget-cash-flow-team-affordability.html`) plus the live-only 2020 CFP.
Their live URLs follow one pattern: `https://plone.org/news-and-events/events/plone-conferences/<edition>/<year>-call-for-proposals` with editions `boston-2016`, `barcelona-2017`, `tokyo-2018`, `ferrara-2019` and `online-2020`.
A local diff of the four archived CFPs shows they are near-identical; the substantive differences are recorded in the rows above (venue floor, streaming wording, the financial requirements added in 2018, the 20 % rate in 2018, and the insurance clause added in 2020).

### Count by status

| Status | Rows |
|---|---|
| verified-current | 20 (R01, R02, R05, R07–R09, R12–R18, R25, R28–R33) |
| verified-changed | 1 (R10) |
| unverifiable | 12 (R03, R04, R06, R11, R19–R24, R26, R27) |
| unverified-pending-Foundation-ask | 4 (R34–R37) |
| Total | 37 |

Caution: `verified-current` confirms that a live page states the item today.
It does not confirm that the Foundation enforces it, and pages such as the financial policy carry no review date.

## Conference Committee — finding

The Conference Committee exists and is current as of 2026-11-02.
Source: https://plone.org/community/teams/conference (fetched live 2026-11-02; identical to `BIB/general-and-current-planning-resources/conference-committee.html`).

- **Mandate:** "The main responsibility of the Conference Committe is to ensure that each year's Plone Conference is successful."
- **Role:** its members "include past conference organizers who keep alive the knowledge of how to organize and host the conference, such as what has to be done when, processes, checklists, people and vendors", and it "provides continuity to each year's organizing team".
- **Membership rule:** open to "interested Plone community members who have experience organizing conferences and sprints"; the committee "is ongoing".
- **Members "for 2026":** T. Kim Nguyen (chair), Alex Pilz, Guido Stevens, Martin Peeters, Rikupekka Oksanen, Asko Soukka, Fred van Dijk, Steve Piercy.
- **Contact:** the Conference Committee mailing list, conf@plone.org.
- **Child page:** the Conference Planning Schedule (https://plone.org/community/teams/conference/conference-planning-schedule) is published under the committee and already dated for 2026 ("September 21–27").

What the page does not say: it claims no authority to set or waive requirements.
Binding decisions sit with the Foundation Board (financial policy R07–R09, conference award R03).
The Board's link to the committee is a liaison role: the live 2023 minutes list "Conference - Mikel Larreategi/Martin Peeters" as Board liaisons (https://plone.org/foundation/meetings/minutes/2023/plone-foundation-board-minutes-november-2-2023); the current liaison was not found in the sources read.

Handbook note (D7): cite the page for the member list rather than copying names into the handbook, because the list changes yearly.

## Live verification log (2026-11-02)

Succeeded (11 direct fetches, all HTTP 200, content matched the archived copy where one exists):

1. https://plone.org/community/teams/conference — Conference Committee, matches archive.
2. https://plone.org/community/teams/conference/conference-planning-schedule — matches archive.
3. https://plone.org/foundation/event-sponsorship — matches archive.
4. https://plone.org/foundation/about/materials/foundation-resolutions/conference-naming — matches archive.
5. https://plone.org/news-and-events/events/plone-conferences/ferrara-2019/2019-call-for-proposals — matches archive; still live as a historical page.
6. https://plone.org/news-and-events/events/plone-conferences/online-2020/2020-call-for-proposals — not archived; adds the insurance clause.
7. https://plone.org/foundation/about/materials/foundation-resolutions/plone-event-financial-policy — not archived; standing resolution, approved 26 January 2017.
8. https://plone.org/foundation/meetings — matches archive; member meetings "held once a year, coinciding with the Plone Conference".
9. https://plone.org/news-and-events/news/news-for-2025/plone-foundation-board-2025-priorities — not archived; "Have a written list of requirements to organize Conferences/Sprints/...".
10. https://plone.org/foundation/meetings/minutes/2023/plone-foundation-board-minutes-november-2-2023 — matches archive; "10% donation" and the call for conference guidelines.
11. Two web searches for post-2020 hosting CFPs — found none; found the financial policy resolution and the 2020 CFP.

Not re-fetched (budget): the 2016, 2017 and 2018 CFP pages; their text is near-identical to the 2019 CFP per the local diff, and they are historical in any case.
Failed: none.
No live page returned 404 or a redirect.

## Questions for the Foundation

One ask bundle, to be sent by a human to board@plone.org with a copy to conf@plone.org.
The plan (section 12, D1 and D8) wants the repository transfer, stewardship and committee questions raised together with the requirement questions.
Nothing below has been sent.

1. **D1 — repository transfer:** Would the Board or the Conference Committee acknowledge transferring the Plone Conference Organizers Handbook repository from `syslabcom` to the `plone` GitHub organization at v1?
2. **D8 — stewardship:** Would the Conference Committee accept handbook maintenance as part of each year's organizer duties, carried over the years by the committee?
3. **Committee mandate:** Is the Conference Committee (https://plone.org/community/teams/conference) the body that owns conference requirements, who is the Board's current Conference liaison, and is the 2026 member list being renewed for 2027?
4. **Requirements list (R03–R27):** Does the "written list of requirements to organize Conferences/Sprints" from the Board's 2025 priorities exist, will a new hosting CFP be issued, and may this register serve as that list once confirmed?
5. **R34 — annual meeting (F12):** Does the Foundation require at least a one-hour slot for the annual member meeting and report, and must it be streamed for absent members?
6. **R10 — Foundation contribution:** What is the current Foundation share of registration revenue (15 %, 20 %, a 10 % donation as in 2023, or another form), and is it owed on registration only?
7. **R08, R37 — financial agent and seed money:** Does the Foundation still act as financial agent under the 2017 Plone Event Financial Policy, are its bank and PayPal accounts still available after the treasury transfer, and does it still offer an advance or seed loan against up-front costs as in Seattle 2006?
8. **R36, R35 — ticket seller and VAT (F2):** Does the Foundation still sell conference tickets itself, and does it hold any guidance or experience on organizers (for example universities) that need not charge VAT?
9. **R12 — insurance:** Beyond due diligence, does the Foundation require proof of event insurance from the conference organizer, and is it named as an insured party?
10. **R20–R24 — CFP-era hard requirements:** Do the date window, venue size, airport distance, Wi-Fi and catering requirements from the 2016–2020 CFPs still apply, given that the 2026 edition sold 117 tickets?
