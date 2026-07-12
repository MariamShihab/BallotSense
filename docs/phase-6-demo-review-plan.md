# Phase 6 demo review plan

Last updated: 2026-07-12

## Goal

Verify that the private archive demo is understandable, citation-first, and
not perceived as a voting recommendation before expanding BallotSense beyond
Measure D.

## Review scope

Use the private staging deployment described in
`docs/staging-deployment.md`.

In scope:

- Measure D archive demo flow.
- Contest selection and fixed issue-lens selection.
- Cited brief display.
- Source-proof disclosure.
- Evidence-gap states.
- Private local note behavior.
- Mobile and desktop usability.
- Keyboard navigation and basic accessibility checks.

Out of scope:

- Public deployment.
- Firestore security-rule changes.
- Production secrets.
- Ballot image upload or OCR.
- Address-based ballot discovery.
- Durable voter profile or account creation.

## Tester profile

Run 3-5 short sessions with people who vary across:

- Familiarity with local elections.
- Comfort reading ballot materials.
- Mobile vs desktop preference.
- Technical comfort.

Do not record personal ballot choices, party affiliation, address, or political
preference. Record only consented usability feedback about the product.

## Moderator script

Use this opening:

> This is an early private demo of BallotSense. It is meant to help people read
> reviewed election material with citations. It is not a voting recommendation.
> Please think out loud while using it. You do not need to share how you would
> vote.

Ask the tester to complete these tasks:

1. Open the private staging demo.
2. Identify what the product says it is and is not.
3. Select Measure D.
4. Pick one to three issue lenses.
5. Open the cited research brief.
6. Find the proof for one displayed claim.
7. Open the original source.
8. Try a lens with insufficient evidence.
9. Explain what the evidence-gap message means.
10. Use the private session note, then clear it.

## Required comprehension questions

Ask these after the task flow:

1. Does the app seem to recommend how you should vote?
2. What do you think `supported` means here?
3. What do you think `insufficient_evidence` means here?
4. Can you tell what type of source the claim came from?
5. Could you find the source proof without help?
6. Did any wording make the app feel biased or too confident?
7. Did anything feel like it might store personal voting preferences?

## Accessibility pass

Before counting Phase 5 accessibility as complete, verify:

- All interactive controls are reachable by keyboard.
- Focus order follows the visual task order.
- Focus indicators are visible.
- Radio buttons and checkboxes have meaningful labels.
- The research button has an understandable disabled state.
- Source-proof disclosure can be opened and closed by keyboard.
- Link text makes sense out of context.
- Text remains readable on a phone viewport.
- Color is not the only signal for selected or supported states.
- Browser zoom to 200% does not hide critical controls.

## Issue severity

Use these severity levels:

- `P0`: Privacy, security, or citation failure that makes the demo unsafe.
- `P1`: Misleading wording, hidden recommendation perception, broken proof
  opening, or inaccessible core flow.
- `P2`: Confusing but recoverable product wording or layout friction.
- `P3`: Polish issue that does not block comprehension or trust.

Fix all `P0` and `P1` issues before broader demo use. Fix or explicitly defer
`P2` issues before Phase 6 acceptance.

## Phase 6.2 exit criteria

Phase 6.2 is complete when:

- At least 3 tester sessions are logged.
- No tester interprets evidence gaps as opposition without correction.
- Testers can find proof for at least one claim.
- Any hidden-recommendation perception is recorded and triaged.
- Accessibility findings are recorded.
- No personal ballot choice, address, or durable preference is recorded.

