# Phase 6 internal demo review

Date: 2026-07-12

Reviewer: AI-assisted internal review

Environment: private staging frontend through authenticated Cloud Run proxy

## Scope

This was an internal walkthrough of the Phase 6.2 demo-review script. It does
not replace 3-5 real tester sessions because it cannot measure how an actual
voter interprets the product without prompting.

## Tasks exercised

- Opened private staging demo through authenticated proxy.
- Confirmed the first-screen product framing says BallotSense is research
  assistance, not a voting recommendation.
- Selected Measure D with climate/environment and public education lenses.
- Reached the cited research brief.
- Verified the climate/environment finding returned `supported`.
- Opened the source-proof disclosure.
- Verified the original source link is present.
- Verified public education returned an explicit `insufficient_evidence` state.
- Switched to Board of Supervisors, District 1.
- Verified the un-ingested contest returned `not_covered`.
- Confirmed the private local note control is present and not included in the
  brief request path.

## Findings

| ID | Severity | Area | Observation | Fix / status |
| --- | --- | --- | --- | --- |
| IR-001 | P1 | Contest heading | After switching to Board of Supervisors, District 1, the result section still said `Measure D research brief`. This could confuse testers about which contest the evidence gap applies to. | Fixed and verified on private staging by deriving the brief heading from the returned/selected contest. |
| IR-002 | P2 | Source attribution | Source proof displayed raw `elections_office_material` text. Accurate, but not friendly enough for voter comprehension. | Fixed and verified on private staging with human-readable source-type labels. |
| IR-003 | P2 | Accessibility | Wrapped labels appear to make radio buttons and checkboxes reachable by accessible name, but the browser automation surface did not expose raw keyboard event testing. | Needs manual keyboard-only pass or Playwright keyboard check in a fuller accessibility run. |

## Passed checks

- Product promise was visible before interaction.
- No recommendation/ranking language appeared in the generated brief.
- Supported claim exposed source proof.
- Evidence gap appeared as a lack of verified evidence, not as opposition.
- District 1 returned `not_covered` instead of hallucinated candidate evidence.
- Direct source link was available from the proof disclosure.
- `make check` passed after fixes.
- Private staging revision `ballotsense-web-staging-00004-qnx` shows the
  corrected District 1 brief heading and readable source type label.

## Still required before Phase 6.2 completion

- Run at least 3 real tester sessions.
- Confirm testers understand research support vs endorsement.
- Confirm testers can distinguish source types after the source-label fix.
- Confirm testers understand `insufficient_evidence` and `not_covered`.
- Complete a keyboard-only accessibility pass.
- Complete a 200% browser zoom check.
