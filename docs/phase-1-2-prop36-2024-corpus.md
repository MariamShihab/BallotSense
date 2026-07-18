# Phase 1–2 pivot: archived California November 2024 Proposition 36 corpus

## Current target

BallotSense is now preparing an **Archived California November 2024 Proposition
36 demo corpus** so the product can keep moving without waiting for November
2026 voter-guide materials.

The source of truth for this corpus is the California Secretary of State's
official November 5, 2024 Voter Information Guide, specifically the pages that
cover Proposition 36's title and summary, Legislative Analyst's analysis,
arguments and rebuttals, and full measure text.

Canonical source:
<https://vig.cdn.sos.ca.gov/2024/general/pdf/complete-vig.pdf>

Archive landing page:
<https://vigarchive.sos.ca.gov/2024/general/>

## Authenticity anchor

The complete official PDF is the primary source artifact. BallotSense snapshots
that PDF first, computes a SHA-256 hash over the exact bytes, and records a
manifest before extraction.

Committed manifest:
`data/source_snapshots/ca-general-2024-11-05/ca-prop-36-2024/master-pdf-manifest.json`

The PDF file itself is intentionally ignored by git. It is a large official
artifact that should be stored locally for development and in the approved
private source-snapshot artifact store for durable operation. The committed
manifest is the auditable reference.

## Review-gated ingestion order

1. Snapshot the official PDF.
2. Hash the exact PDF bytes.
3. Write the master PDF manifest.
4. Extract page-level verbatim chunk candidates.
5. Keep source records and review packets in `pending` state.
6. Human reviewer compares each chunk to the official PDF.
7. Only approved chunks are promoted into `data/corpus`.
8. Only promoted chunks may be ingested into Firestore.
9. Only ingested approved chunks may receive embeddings.

## Local commands

```bash
make snapshot-prop36-source
make prepare-prop36-review
make promote-prop36-review
```

`make promote-prop36-review` must fail until the review packet is explicitly
approved. That failure is expected and protects the retrieval corpus from
unreviewed extraction output.

## Phase 3 handoff condition

The Ballot scanner UI may begin after the Phase 1–2 structure exists. The scanner
must initially detect and confirm ballot entities only. It must not store ballot
images, infer voter selections, or generate voter-facing answers from unapproved
chunks.
