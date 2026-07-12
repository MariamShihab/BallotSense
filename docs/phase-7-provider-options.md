# Phase 7 provider options — address-to-contest discovery

Date: 2026-07-12

## Decision needed

BallotSense can now accept an address for a single live request, but it does
not infer contests until the project owner approves a provider. This note
compares the realistic provider/source options for Santa Clara County.

## Options reviewed

### Option A — Santa Clara County ROV district finder

Source:

- Santa Clara County Registrar of Voters, “Look Up Your District”
- Service URL reached from the County page:
  `https://rovservices.sccgov.org/Home/IndexPost?selected=dt&distance=0&navtab=pm&asm=simple&selectedLanguageId=22`

What it provides:

- Residential-address lookup.
- District, precinct, supervisorial district, council district, and district
  offices for the precinct.

Pros:

- Best attribution: official County ROV source.
- Best fit for “which districts am I in?”
- Useful for confirming whether a voter is in a district race such as Board of
  Supervisors District 1.

Cons:

- It appears to be a browser-facing JavaScript service, not a documented public
  API.
- Scraping or automating the form would be brittle and may violate the spirit
  of the service.
- It returns districts/offices, not necessarily the full contest list for a
  specific election.

Recommendation:

- Use as a cited reference and manual fallback link now.
- Do not automate against it unless the County provides permission, API
  documentation, or a stable export.

### Option B — Santa Clara County ROV sample-ballot / “What’s on Your Ballot” service

Source:

- Santa Clara County Registrar of Voters, “See What’s on Your Ballot”
- The ROV services portal includes “View Sample Ballot” and “View Voter Info
  Guide” flows.

What it provides:

- The most semantically correct user outcome: what appears on a voter’s ballot.

Pros:

- Official County ROV source.
- Better than district lookup if the goal is contest discovery, not merely
  district discovery.
- Could reduce mapping errors between districts and contests.

Cons:

- Also appears browser-facing rather than a documented public API.
- May require voter-specific fields beyond address in some flows.
- Should not be scraped without explicit approval.

Recommendation:

- Best official target if the County can provide a stable API/export.
- Until then, provide a user-facing link rather than automated integration.

### Option C — Google Civic Information API / Voting Information Project

Source:

- Google Civic Information API `voterInfoQuery`

What it provides:

- Address-based voter information.
- Polling locations, drop boxes, election officials, and contests.
- Optional `electionId` and `officialOnly=true`.

Pros:

- Documented API.
- Returns structured contests.
- Supports backend integration with API-key restrictions.
- Faster to implement than building geospatial precinct matching ourselves.

Cons:

- User address is sent to Google, not only to BallotSense.
- Data availability depends on election coverage and timing.
- It is an aggregator; even with official-source flags, BallotSense should
  still disclose the provider and require user confirmation.
- Requires an API key and Secret Manager configuration.

Recommendation:

- Acceptable only if the UI explicitly says the address will be sent to Google
  for ballot lookup, and only if the user confirms before submitting.
- Use `officialOnly=true`, always require confirmation, never persist the
  address or normalized address, and keep manual contest selection available.

### Option D — Build our own GIS/precinct resolver from public boundary data

What it provides:

- Potentially self-contained address-to-precinct/district resolution.

Pros:

- Strong privacy if addresses are geocoded in-memory and no third party is
  called after setup.
- More controllable and auditable once built.

Cons:

- Requires authoritative precinct/district boundary data and address geocoding.
- Easy to get wrong at district boundaries.
- Higher maintenance burden after redistricting or election-specific precinct
  changes.
- Not worth it for the archive demo.

Recommendation:

- Do not build this for the MVP.

## Recommended path

For the archive demo:

1. Keep manual contest selection as the default.
2. Add official outbound links to:
   - County ROV “Look Up Your District”
   - County ROV “What’s on Your Ballot” / sample ballot service
3. Do not automate address lookup until we have either:
   - a County-approved API/export, or
   - explicit approval to use Google Civic with user consent.

For a future real election demo:

1. First ask Santa Clara County ROV whether a documented address-to-ballot or
   address-to-district API/export is available.
2. If not, use Google Civic only as a consent-gated fallback:
   - backend-only API key in Secret Manager
   - `officialOnly=true`
   - election ID pinned
   - no address logging
   - no address/normalized-address persistence
   - mandatory user confirmation before any research request
3. Continue treating manual contest selection as the safety fallback.

## Current decision status

Approved decision as of 2026-07-12:

> Keep Phase 7.1 manual-only for the archive demo, with official ROV links.
> Do not enable automated address lookup yet.

Implementation can proceed with a small UI update that labels address discovery
as “not enabled for this archive demo” and points users to the official County
ROV lookup pages.
