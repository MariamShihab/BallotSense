# Deferred features and intentionally omitted scope

Date started: 2026-07-12

This is the running list of features BallotSense deliberately did **not**
implement in the archive demo. Items on this list are not forgotten; they are
future decisions that require separate product, privacy, source, and safety
review before implementation.

## Deferred for the archive demo

| Feature | Status | Why omitted now | Reconsider when |
| --- | --- | --- | --- |
| Numeric match score or candidate ranking | Omitted | Could look like an endorsement and hide uncertainty. The product promise is cited research assistance, not a voting recommendation. | Only if there is a reviewed, explainable, non-endorsement framing that survives user testing. |
| Free-text political values input | Omitted | Free text increases privacy risk and makes retrieval/generation harder to audit. | After fixed issue lenses, citation validation, and abstention behavior are trusted. |
| Durable voter profile or account | Omitted | The demo does not need accounts, and durable profiles would create sensitive voter-preference data. | Only with a separate privacy/security design and explicit user value. |
| Backend ballot image upload | Omitted for archive demo | Ballot images can be sensitive, especially if marked or personally identifying. The Phase 3 scanner shell previews images in browser memory only. | Only if the team proves in-memory-only backend handling, no logs/storage, red-team tests, and a disable switch. |
| Ballot OCR / scan-to-contest extraction | Deferred after scanner UI shell | The UI can preview an image in browser memory, but no image is uploaded, stored, logged, or processed by OCR yet. | Reconsider after the Prop 36 corpus review gate and privacy contract are ready. |
| Automated address lookup | Manual-only for archive demo | Official County tools appear browser-facing, not a documented API; scraping would be brittle. Google Civic would send the address to a third party. | If Santa Clara County provides an approved API/export, or if the user explicitly approves Google Civic with consent UI. |
| Whole-ballot coverage | Omitted | The reviewed corpus only covers a small archive-demo scope. Whole-ballot coverage would imply completeness we do not have. | After Phase 8 builds and approves a release-candidate corpus for a specific election/geography. |
| Board of Supervisors District 1 candidate evidence | Shell only; corpus not added | The candidate race was selected as the next demo contest, but reviewed candidate sources have not been ingested. | After official candidate statements and other approved sources are gathered, reviewed, chunked, embedded, and evaluated. |
| Campaign-material ingestion beyond approved Measure D materials | Omitted | Campaign claims and official election materials should not be silently treated as equivalent. | After source policy labels, reviewer workflow, and attribution UI are ready for campaign sources. |
| Public deployment | Omitted | Staging is private; public release requires corpus coverage, security, load/cost, incident, correction, and go/no-go checks. | Phase 8 public-release decision. |

## Current Phase 7 decision

Approved on 2026-07-12:

> Skip backend OCR and ballot image uploads for the archive demo. A later
> scanner UI shell may preview an image in browser memory only, but contest
> selection remains manual/confirmed and official lookup links remain available.

## Maintenance rule

Whenever BallotSense chooses not to implement a tempting feature, add it here
with:

1. the omitted feature,
2. the reason,
3. what evidence or approval would be needed to reconsider it.
