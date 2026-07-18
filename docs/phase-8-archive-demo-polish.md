# Phase 8 archive demo polish pass

Date: 2026-07-18

## Context

The November 3, 2026 official voter-guide package is not published yet, so
Proposition 1 and Proposition 45 remain monitor-only. While the release-candidate
corpus is blocked by the official publication calendar, the archive demo can be
made clearer and more credible.

## Product intent

The archive demo should quickly communicate:

- this is a narrow June 2026 Measure D archive demo,
- BallotSense is research assistance, not a voting recommendation,
- claims are either backed by reviewed citations or explicitly abstained from,
- ballot images, OCR, address lookup, accounts, and durable profiles are
  intentionally omitted,
- November 2026 source ingestion waits for official voter-guide publication.

## Changes made

- Added clearer archive-demo and Measure D-only labels to the hero.
- Added a "How BallotSense works" section:
  1. reviewed sources first,
  2. lens-specific retrieval,
  3. cited or abstained.
- Added a "What this demo does not do" section for omitted scope.
- Marked Board of Supervisors District 1 as not covered yet instead of making it
  look like a usable demo contest.
- Improved the research brief guidance so insufficient-evidence cards read as
  intentional abstentions rather than app failures.
- Renamed the source-proof disclosure to "Inspect source proof for this claim."
- Preserved the local-only private note and manual official lookup fallback.

## Validation

- `make check-november-sources`
- `npm --prefix web run check`

## Current status

The archive demo is polished enough to continue internal review while Phase 8
waits for official November voter-guide materials.
