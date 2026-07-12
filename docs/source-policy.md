# BallotSense source and citation policy

## Purpose

BallotSense is a cited research assistant. It must not make a factual claim
about a candidate, measure, or voting process unless that claim is connected to
one or more reviewed source chunks in the election corpus.

This policy applies to the archived June 2026 primary demo and to every future
election dataset.

## Review status

The ballot-argument source type was reviewed for the MVP on 2026-07-11. It is
allowed only because officially filed arguments and rebuttals appear in the
official voter guide record. Their claims must always be attributed to the
speaker side and must not be treated as neutral verified facts.

## Source tiers

| Tier | Source type | Allowed use |
| --- | --- | --- |
| 1 | Official ballot, measure text, county/state voter guide, elections-office material | Factual election information and measure descriptions. |
| 2 | Candidate statement filed with an elections office; officially filed ballot argument or rebuttal | The speaker's stated position, always attributed. |
| 3 | Candidate campaign website or official public statement | A candidate's stated position, explicitly attributed and dated. |

News reporting, endorsements, social posts, and third-party scorecards are out
of scope for the MVP corpus. They cannot support a generated comparison claim.

## Review requirements

Every source document must record its publisher, canonical URL, election and
jurisdiction, retrieval time, SHA-256 content hash, source tier, and review
status. A human reviewer must approve it before its chunks may be retrieved.

Every chunk must retain its parent source ID, contest ID where applicable, and
a stable locator such as a page number or heading. Ingestion must preserve the
original text; summaries are never source material.

## Generation requirements

- Generation receives only reviewed retrieved chunks and the user's stated
  priorities.
- Every output claim needs at least one citation to a supplied chunk.
- A citation must identify the source, chunk, and human-readable locator.
- If the corpus does not support a comparison, the response must say that
  verified information was not found. It must not fill the gap with model
  knowledge or inference.
- Candidate and campaign-material statements must be attributed rather than
  presented as independently verified facts.
- Ballot arguments and rebuttals must be identified as an argument in favor of,
  against, or a rebuttal to a measure. Their presence in an official voter guide
  does not make their assertions independently verified facts.

## Privacy

Ballot images are processed in memory and discarded after contest extraction.
They are not source documents and must never be added to the election corpus.
