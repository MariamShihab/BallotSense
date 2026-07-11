# BallotSense

A citation-first voter education platform. BallotSense helps a voter compare
choices through their stated priorities, but never displays a factual claim
without a link back to reviewed election material.

## Pinned project references

- [System design and delivery roadmap](docs/system-design-and-roadmap.md)
- [Source and citation policy](docs/source-policy.md)

## Current milestone

We are building the trust layer against an archived June 2026 primary dataset.
That lets us test sourcing, review, retrieval, citations, and OCR confirmation
before considering a public November 2026 experience.

The product does **not** tell a voter how to vote. It presents cited,
attributed comparisons and says when verified information is unavailable.

## Repository layout

- `docs/source-policy.md` — source tiers, human-review rules, citation rules,
  and ballot-image privacy rules.
- `ballotsense_api/` — FastAPI contracts and source-catalog endpoints.
- `tests/` — checks that claims cannot be constructed without citations and
  approved sources require a recorded review time.

## Run locally

Create a virtual environment, then install the project with its development
dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn ballotsense_api.main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

Run checks with:

```bash
pytest
```

## Next

1. Ingest and human-review official June 2026 documents into Firestore.
2. Build contest-level retrieval that returns only approved chunks.
3. Require structured, cited output from the generation layer.
4. Add ballot-photo OCR with user confirmation and in-memory-only image handling.
