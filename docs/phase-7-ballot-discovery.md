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

## Next decision

Choose the official address-to-district provider/source for Santa Clara County
or decide to keep manual contest selection only for the archive demo.
