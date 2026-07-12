# Phase 8 November 2026 release-candidate corpus plan

Date created: 2026-07-12

## Purpose

Phase 8 decides whether BallotSense should move beyond the private archive demo
into a November 3, 2026 release-candidate corpus. This is a planning and
go/no-go phase, not a launch commitment.

The rule is simple: no public release unless the corpus is official, reviewed,
cited, evaluated, scoped honestly, and operationally safe.

## Official anchors to monitor

Initial official sources:

- California Secretary of State, General Election — November 3, 2026:
  `https://www.sos.ca.gov/elections/upcoming-elections/general-election-november-3-2026`
- California Secretary of State, Qualified Statewide Ballot Measures:
  `https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures`
- Santa Clara County Registrar of Voters home:
  `https://vote.santaclaracounty.gov/home`
- Santa Clara County Registrar of Voters district lookup:
  `https://vote.santaclaracounty.gov/look-your-district`

Current verified facts from official sources:

- The target statewide general election date is November 3, 2026.
- California active registered voters receive ballots for the November 3, 2026
  General Election.
- County elections officials begin mailing ballots by October 5, 2026.
- The California Secretary of State maintains a qualified statewide ballot
  measures page for November 3, 2026.

## Proposed initial public-demo scope

Recommended scope for the first release-candidate corpus:

1. Santa Clara County voter-facing demo.
2. One to two statewide ballot measures only: Proposition 1 as primary target,
   Proposition 45 as secondary target.
3. No candidate races until the measure flow passes release-candidate review.
4. No whole-ballot claim.
5. No automated address lookup.
6. No ballot image upload or OCR.

Why measures first:

- Official measure text, title/summaries, fiscal analyses, and arguments are
  usually easier to cite cleanly than candidate positions.
- Measures reduce the risk that BallotSense is perceived as ranking candidates.
- They let us test source coverage, citation display, evidence gaps, and
  correction handling without expanding into a large candidate corpus.

## Candidate source inventory targets

For each proposed November measure, create source records only after official
materials are available. Candidate source types:

| Source type | Expected publisher | Required before retrieval? |
| --- | --- | --- |
| Official measure text | California Secretary of State or county election office | Yes |
| Official title and summary | California Secretary of State / Attorney General / county election office | Yes |
| Legislative Analyst/fiscal analysis | California Secretary of State voter guide or linked official analysis | Strongly preferred |
| Official voter guide arguments | California Secretary of State or county voter guide | Required if displayed |
| Rebuttals | California Secretary of State or county voter guide | Required if displayed |
| Campaign material | Campaign committees | Optional; must be clearly labeled and not mixed with neutral official material |

Do not ingest news articles, commentary, endorsements, social media, or
unreviewed campaign pages for the first release-candidate corpus.

## Measure selection rules

Before selecting the first one or two measures:

1. Confirm the measure appears on the official November 3, 2026 qualified list
   or official voter guide.
2. Confirm official text and title/summary are available.
3. Confirm at least one neutral official explanatory source is available.
4. Confirm source locators are stable enough for citation display.
5. Confirm the source reviewer approves the inclusion.

Recommended first pass:

- Build a metadata-only inventory of all qualified statewide measures.
- Score each measure for source completeness, locator quality, and issue-lens
  fit.
- Select Proposition 1 as the primary target and Proposition 45 as the
  secondary target, pending official voter guide source completeness.

## Coverage matrix requirements

For every candidate release-candidate measure, create a coverage matrix with:

- measure ID and official title,
- source types available,
- source tiers,
- issue-lens coverage,
- known evidence gaps,
- source attribution notes,
- reviewer status,
- decision: `include`, `defer`, or `exclude`.

The UI must publish this scope plainly. If BallotSense covers only two measures,
it must say it covers only two measures.

## Review workflow

Repeat the Phase 2 source workflow:

1. Gather source candidates.
2. Snapshot and hash approved-to-review source artifacts.
3. Extract verbatim chunks only.
4. Preserve source URL, publisher, date, retrieval timestamp, page/heading
   locator, election ID, contest/measure ID, reviewer, and review status.
5. Human-review each source and chunk.
6. Promote only approved chunks to retrieval.
7. Create a deliberate evidence-gap fixture.

No embeddings, retrieval, or Gemini voter-facing answers may run until the
approved corpus passes the checklist.

## Evaluation requirements

Before public/demo release:

- Every display claim has an approved citation.
- Wrong-measure and wrong-election chunks cannot be retrieved.
- Rejected and pending-review chunks cannot be retrieved.
- Evidence gaps display as gaps, not negative inferences.
- Campaign/argument source labels are unmistakable.
- No recommendation, ranking, or match score appears.
- Accessibility checks pass for the release-candidate UI.
- Correction workflow works against the release-candidate corpus.

## Privacy and operations requirements

The release candidate must still omit:

- ballot image upload,
- OCR,
- durable voter profiles,
- account creation,
- automated address lookup unless separately approved,
- storage of voter selections or local notes.

Before any public endpoint:

- Confirm Cloud Run scale limits and rollback.
- Confirm budget alerts.
- Confirm logging does not contain addresses, notes, prompts with voter data,
  ballot images, or voter selections.
- Confirm correction owner and incident-response owner.
- Confirm source reviewer sign-off.

## Go/no-go checklist

Launch or public demo only if all are true:

- [ ] Exact geography and covered contests are published in the UI.
- [ ] Every included measure has official reviewed sources.
- [ ] Every approved source has URL, publisher, hash, retrieval time, source
      tier, reviewer, and review state.
- [ ] Every displayed claim has an approved citation.
- [ ] Evidence gaps render correctly.
- [ ] No ballot image, address, account, or durable preference path is enabled.
- [ ] Evaluation passes with zero unsupported display claims.
- [ ] Accessibility and mobile checks pass.
- [ ] Correction workflow is live and monitored.
- [ ] Rollback is tested.
- [ ] Product owner and source reviewer approve the release candidate.

If any item is false, keep the archive demo, document the gap, and defer public
release.

## Immediate next actions

1. [x] Build a metadata-only inventory of November 3, 2026 statewide measures
   from official SOS sources.
2. [x] Identify initial watchlist measures based on source completeness and
   issue-lens fit.
3. [x] Recommend one or two measures for the first release-candidate corpus:
   Proposition 1 primary, Proposition 45 secondary.
4. [x] Check source readiness for Proposition 1 and Proposition 45.
5. [ ] Ask the project owner/source reviewer to approve the selected scope before
   snapshotting or ingestion.

Current readiness result as of 2026-07-12: monitor only. Qualified-measure
listings and underlying measure text are available. The official voter-guide
page exists at `https://voterguide.sos.ca.gov/`, but says the November 3, 2026
guide will be available in September 2026. Arguments, rebuttals, analyses, and
stable voter-guide locators are therefore not ready for release-candidate
ingestion.

To re-check:

```bash
make check-november-sources
```
