# Source-candidate review queue

Files in this directory contain **metadata only** for election sources that a
reviewer may evaluate. They are not the BallotSense corpus.

Before a source candidate becomes retrievable, the source reviewer must:

1. Confirm that the canonical URL and publisher are correct.
2. Confirm its election, jurisdiction, contest, source type, and attribution.
3. Fetch and snapshot the exact approved document in the designated artifact
   store.
4. Record the snapshot SHA-256, retrieval time, and reviewer decision in an
   approved `SourceDocument` record.
5. Extract reviewable, verbatim chunks with stable locators.
6. Approve chunks individually before embeddings or retrieval are allowed.

Do not place raw voter ballot images, personal addresses, voter choices, or
unreviewed extracted chunks in this directory.
