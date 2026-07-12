# Phase 7 ballot discovery notes

Date: 2026-07-12

## Current implementation

BallotSense now has the privacy-safe address-discovery interface, but no live
geographic provider is configured yet.

Implemented:

- `POST /v1/ballots/resolve-address`
- Strict request/response contracts for ephemeral address resolution
- Default provider-not-configured resolver
- Frontend proxy route
- Voter-facing optional address-discovery panel
- Manual contest picker remains available
- Automated tests proving:
  - extra voter-profile fields are rejected
  - the response never includes or retains the raw address
  - an unconfigured provider cannot infer contests
  - any discovered contest path requires user confirmation

## Privacy stance

The raw address is accepted only for a single request. It must not be stored in
Firestore, Cloud Storage, claim audits, correction reports, logs, model prompts,
or analytics. The current default resolver deliberately does not inspect or
normalize the address.

## Provider gate

Before BallotSense can infer contests from an address, the project owner must
approve an official jurisdiction source or address-to-district provider. Until
then, the API returns `provider_not_configured` with manual fallback contests.

## Verification

`make check` passed on 2026-07-12:

- Ruff passed
- 40 backend tests passed
- Web typecheck passed
- Web production build passed
- Playwright + axe accessibility test passed

## Provider decision

Approved on 2026-07-12: keep the archive demo manual-only and do not enable
automated address lookup.

See [Phase 7 provider options](phase-7-provider-options.md). The recommended
current decision is to keep the archive demo manual-only and link to official
County ROV lookup pages rather than scraping a browser-facing lookup service.

## OCR and ballot-image decision

Approved on 2026-07-12: skip OCR and ballot image uploads for the archive demo.

Rationale:

- The archive demo already has manual contest selection.
- Ballot images are sensitive, especially if a voter uploads a marked ballot or
  personally identifying material.
- OCR would add image type limits, size limits, in-memory handling guarantees,
  no-storage tests, red-team marked-ballot tests, and a feature flag before it
  could be responsibly enabled.
- The demo does not need scan-to-contest convenience to prove the citation-first
  research experience.

This omission is tracked in [deferred features](deferred-features.md).

## Phase 8 transition

Phase 7 archive-demo scope is complete after this decision. The next planning
phase is Phase 8: decide whether and how to build a November 3, 2026
release-candidate corpus.
