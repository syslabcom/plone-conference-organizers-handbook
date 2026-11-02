# Plone Conference 2026 — Attendee Survey Analysis

Analysis of the 21 feedback-form submissions received after Plone Conference 2026 (Maastricht, 21–27 September 2026). The raw submissions live in this directory as `.eml` files; they contain personal identifiers, are excluded from version control (see `.gitignore`), and stay private. This document is anonymized — respondents appear as R1–R21 following the file order; the mapping is only meaningful to someone holding the raw files.

- **Source:** 21 form submissions, received 12–30 October 2026
- **Response rate:** 21 responses against 117 tickets (five of them party-only) — roughly one in five attendees
- **Method:** deterministic extraction of every submission into structured data, then aggregation by script; every rating and count below is reproducible from the extraction (see appendix)
- **Sample caveat:** respondents skew towards insiders. Of the 11 respondents who answered the relationship-to-Plone question, 10 were already active in the community — but that question reached only half the sample, and 9 of its 11 answerers were Business Track attendees (see appendix). 14 of 20 had their ticket paid by an employer. Read the results as the voice of the engaged community, not of the new audiences the conference tried to reach.

## Ratings at a glance (1–5 scale)

| Area | n | Mean | Median | Distribution (1→5) |
|---|---|---|---|---|
| Food & catering | 21 | 4.81 | 5 | 0 / 0 / 0 / 4 / 17 |
| Organising & logistics | 21 | 4.62 | 5 | 0 / 0 / 1 / 6 / 14 |
| **Overall feeling** | 21 | **4.57** | 5 | 0 / 0 / 3 / 3 / 15 |
| Training | 13 | 4.31 | 5 | 1 / 0 / 1 / 3 / 8 |
| Value for money | 20 | 4.30 | 4.5 | 0 / 0 / 4 / 6 / 10 |
| Keynotes & talks | 21 | 4.24 | 4 | 0 / 0 / 4 / 8 / 9 |
| Business Track | 8 | 4.12 | 4 | 0 / 0 / 1 / 5 / 2 |
| Party & socialising | 19 | 4.11 | 4 | 0 / 1 / 4 / 6 / 8 |

All 21 respondents attended the three conference days; 17 attended trainings, 14 the sprints, 9 the Business Track. For 2027 in Bucharest: 16 said YES, 2 Perhaps, 3 Probably not. Across the whole dataset there are exactly two ratings below 3: one 1 (Training) and one 2 (Party).

## Findings by area

### The venue bet worked — with one structural cost

The hotel venue is the strongest theme in the free-text answers; eleven respondents wrote about it. The majority praise having conference, rooms, and catering in one building. R15: "It saved me time and allowed me to be more rested." R16 contrasts the venue with past Plone Conference venues on wifi, temperature, and seating, and separately praises the on-site lunches and the options for dietary restrictions. R11 calls the catering the "best ever in a Plone Conference". Food & catering (4.81, no rating below 4) is the best-scored area of the conference.

The cost is social, not operational. The hotel was pricey — named by R9 ("very expensive"), R11 ("Rather expensive hotel, but so good"), and R14, who stayed elsewhere because of it — and it sat far from the centre. Most attendees did not stay on site: only 5 of 20 did (all five would stay again). R3 and R9 describe the consequence: evening socialising became harder. R3: "the hotel was far from other hotels and the town center. Socializing after the conference was quite difficult." R14 agrees the venue felt "detached from everything else in the City center". One counterpoint: R11 found the centre "equally easy to reach", and R3 — despite the complaint — stayed at the hotel and would again. Distance and price were real frictions, but they did not ruin anyone's week.

Party & socialising (4.11) is the joint-lowest rating, effectively tied with the Business Track (4.12, though on only 8 responses). Two of the three respondents with an overall score of 3 also gave the party a 3 or lower (R1: 3, R16: 3; the third, R7, skipped the question and gave keynotes a 3). The evidence on the venue's role is thin and mixed: the party's one 2 comes from R3 — the respondent who wrote most directly about difficult after-hours socialising — while the other two distance writers, R9 and R14, rated the party 5 and 4. Since the party was an off-site event, the survey cannot separate venue effects from the evening itself.

### Organisation and accessibility landed

Organising & logistics scored 4.62 with fourteen 5s and a single 3 (R3). R1's keep-doing: "Keep being accessible. It helps that the organisers are just an email away."

### Trainings: high average, one sharp failure

Seventeen respondents attended trainings; 13 rated them (R7, R11, R12, R21 attended without rating). The 13 ratings average 4.31 with eight 5s. They also hold the only 1 in the entire dataset. R16: "The trainings I attended were a huge disappointment. I learned nothing, and I expected some hands on work. Stop allowing trainings that don't actually do training." R16 also rated keynotes 3 and party 3 and leans against Bucharest, so this is a generally cooler respondent, and R9 does praise "the trainings and sprints" in general terms — but no respondent identifies specific sessions, so R16's specific complaint stands unanswered by an equally specific defence. A hands-on quality floor for trainings is the clearest single programme action in the data.

### Business Track: a clear yes to returning — from providers, preferably shorter

Nine respondents attended the Business Track; eight rated it (mean 4.12; R14 attended without rating). All nine who answered want it back in 2027, with five preferring a shorter format over a full day.

Who showed up matters more than the score. Of the nine attendees, seven earn their living providing Plone services; only R8 and R18 do not. The roles overlap — five of the nine, including three of the providers, also ticked working at an organisation that uses Plone — and the survey does not measure seniority, so how many decision-makers were in the room is simply unmeasured. Six of the nine came because they were "already attending"; three came for the topic. (A tenth respondent, R6, answered the what-brought-you question without having attended the track.) The survey-visible audience was therefore mostly providers talking to providers, on a track designed to reach customers. One attendee who also spoke, paraphrased for privacy, found the format valuable for the providers on stage, observed a smaller decision-maker audience than hoped, and asked for scheduling that lets speakers attend the discussions. R1 raises the general version of the same scheduling flaw: speakers could not attend roundtables and panel discussions because of overlapping slots.

### Content balance: a genuine, unresolved disagreement

The audience profile is clear: of 18 respondents, 9 come technology-first with an appreciation of context and business talks, 6 come equally for both, 2 want deep technical content only, and 1 came primarily for business and strategy. Against that profile, the tech/business mix draws both a keep and two stops. R6 wants to keep "interesting keynotes that broaden the mind"; R3 wants to stop "keynotes that are not related to IT at all"; R7 goes further: stop "any talks that involve AI". The majority wants the mix; a vocal minority draws the line at non-IT keynotes and AI.

### Value for money: four 3s, and the data does not explain them

Four respondents rated value for money 3 (R1, R3, R12, R20). None of them wrote anything about price in their free text, and no respondent anywhere in the survey mentioned the ticket price. Venue and hotel cost were criticised — but by R9, R11, and R14, who rated value for money 4, 5, and 4 respectively. The three self-paid attendees (R6, R15, R16) rated value for money 4, 5, and 4 — at least as satisfied as the average. All four value-3 raters had employer-paid tickets, though that explains little: not paying yourself is the norm in this sample (17 of 20). The only co-occurrence in the data is that three of the four value-3 raters also rated the party 3 or lower (R1, R3, R12; R20 rated it 4) and two rated keynotes 3 (R3, R20) — cooler party and keynote ratings rather than a price statement, on numbers far too small to settle. An honest summary: the survey contains no articulated reason for the four low value scores.

### Small operational wishes, cheaply fixable

- Double-sided badge printing (R15, R21 — two independent mentions)
- Speaker introductions that include background, not just a name (R15)
- Per-talk feedback forms (R15)
- Lightning talks at 3 minutes instead of 5 (R21)
- Earlier website, advertising, and ticket sales for the next edition (R11)
- Guided evening socialising: R16 asks for organised dinners on training and sprint days, R6 for suggested areas per evening, R9 for planned social activities and a restaurant list
- Invite students and younger developers to the training days (R9)

### T-shirts drew two specific criticisms

R6 asks for less conspicuously lettered, more artistic shirts that get worn for years, citing Seattle and Budapest as the shirts they wore most. R9 asks for no female-cut shirts. Both land directly on 2026 production choices and belong in the 2027 print brief.

## Consolidated start / keep / stop

**Start:** fix the speaker/panel scheduling overlap · organised or guided evening socialising, including training and sprint days · university outreach · earlier ticket sales and site · double-sided badges · per-talk feedback · speaker intros with background · 3-minute lightning talks · (one vote) a co-located PyCon day.

**Keep:** organiser accessibility · the Aurora/Blicca parallel structure · the tech/non-tech mix · food standard, pace, open spaces, talk buffers · the party · the Business Track · the trainings and sprints · community and marketing.

**Stop:** non-IT keynotes (1) · AI talks (1) · trainings that do not train (1) · conspicuous shirt lettering (1) · female-cut shirts (1) · single-sided badges (1) · spreading developer efforts (1).

## Interpretation — what this means for the post-mortem and 2027

This section is my reading of the data, not the data itself. Where a claim goes beyond what the numbers show, it says so.

1. **The conference delivered for the people it already serves.** A 4.57 overall with 15 of 21 at the top score, 16 of 21 intending towards Bucharest, and only two sub-3 ratings anywhere: the core event worked. But this survey is a community pulse, not a market signal. The respondents we can profile are mostly established community members on employer-paid tickets. Whether the conference reached beyond the community, this data cannot say — the people we failed to attract did not fill in the form, and half the sample did not even see or answer the relationship question.

2. **The Business Track's real outcome differs from its stated goal — and is still worth keeping.** It was designed to reach decision-makers ("no prior Plone knowledge required"); its survey-visible audience identifies mostly as providers, the majority of whom were at the conference anyway — how many decision-makers were actually in the room, the survey cannot say. What it produced, on the evidence of one speaker-attendee, is provider confidence — people who sell Plone practising that sale in front of peers. That is a real outcome, but it is not demonstrated market access. My read: keep the format, shorten it as the majority of its own attendees prefer, fix the scheduling so providers can attend their own track's discussions, and judge the 2027 edition by a metric we can observe — registrations from outside the community — rather than by intent.

3. **The venue trade-off is real but narrower than it first looks.** The hotel delivered the best catering and logistics scores of the conference and a working "Plone bubble", and its price and location made evening socialising harder for at least the two respondents who wrote about it — that much the free text shows directly. On the party rating the evidence is thin and genuinely mixed: R3, the sharpest distance critic, gave the party its only 2, while the other two distance writers rated it 5 and 4 — and the party was an off-site event with its own merits, so venue and evening effects cannot be separated here. The solid, actionable signal is that three respondents independently asked for engineered evenings — organised dinners on training and sprint days, suggested areas, restaurant lists. For Bucharest: pick a venue reachable from where people actually sleep, and treat evening programming as an organised deliverable, not a self-organising afterthought. That is the cheapest large satisfaction gain available.

4. **Trainings need a quality floor.** The only 1 in the dataset came from a hands-on expectation that was not met, and the accompanying stop-doing is unambiguous. A simple contract for 2027 trainers — hands-on exercises, stated prerequisites, stated outcomes — removes the sharpest single failure mode in the data. One respondent is not a trend; but the fix costs almost nothing, and nothing in the 13 training ratings contradicts it.

5. **Price perception is a blind spot, not a confirmed problem.** I initially read the four value-for-money 3s as venue-cost driven; the data contradicts that. The cost complaints come from satisfied respondents, the low value scores come with no stated reason and travel with cooler party and keynote ratings rather than with any price remark, the self-paid attendees are content, and nobody mentioned the ticket price. The defensible conclusions are narrow: the ticket price is not an observed issue, hotel prices are a noted annoyance that did not determine satisfaction, and the 2027 survey should ask about price perception directly instead of leaving us to guess.

6. **Protect the minority voices without letting them set the programme.** The "stop AI talks" and "stop non-IT keynotes" voices are a minority — the why-attend profile wants the mix, and one keep-doing praises exactly the broadening keynotes another respondent would cut. That profile is itself survivor-biased: its three skippers (R7, R13, R16) are exactly the three "Probably not" for 2027, and one of them (R13) rated the conference 5 overall — so return intent measures more than satisfaction, and the happiest-looking profile excludes precisely the people drifting away. The two sharp critics overlap with the intent not to return: the AI skeptic (R7) and the disappointed training attendee (R16), while the non-IT-keynote critic (R3) still plans to come. The following is my opinion, not a data finding: keep the broadening keynotes and the practical AI content, make the technical core unmistakably strong, and never let AI become the conference's identity rather than one topic among many.

7. **The survey itself needs redesign.** The free-text fields were too small to write in — R11 said so inside an answer — there was no general comment field, the relationship-to-Plone question reached only 11 of 21 respondents, and nothing in the form would catch the people we failed to attract. For 2027: larger text fields, one open final field, an explicit price-perception question, a question about what nearly stopped you from coming, and a short version sent to community members who did not attend.

## Appendix — method, reproducibility, privacy

- Raw data: 21 `.eml` files in this directory (form submissions via plone.org, 12–30 October 2026). They contain respondent email addresses in six cases, are covered by a `.gitignore` rule, and must never be committed or republished. Respondent IDs follow the file order; the mapping is only usable with the raw files.
- Reproduction: the extraction and aggregation scripts live in `aftermath/survey/data/` (`extract.py`, `aggregate.py`). From the repository root: `python3 aftermath/survey/data/extract.py` (writes to the git-ignored `tmp/survey-extract/` — the JSON contains personal identifiers, which is why the default output location is ignored), then `python3 aftermath/survey/data/aggregate.py tmp/survey-extract`. Every rating, distribution, and count in this document appears in the aggregate output. The full session journal, including the complete free-text corpus printout (`aggregate.txt`), is in `.omo/ulw-research/20261102-092527/`. Dates and the ticket total come from the mail headers and `planning/sales-data/final-tito.xlsx` respectively. No sanitised dataset is checked in: the quoted free text can re-identify respondents to insiders, so the raw mails remain the only regeneration source.
- Skip patterns are properties of the original form, not extraction artifacts — verified in the question census (`census.txt`): training ratings came from 13 of 21, the Business Track block from 8–10, the hotel follow-up from exactly the 5 hotel stayers, and the relationship-to-Plone question from only 11.
- This document went through three red-team review rounds; the first draft's value-for-money and party-rating interpretations were contradicted by the data and have been rewritten, and several counts, attributions, and role statements were corrected across rounds two and three. The review trail is in the session journal.
