"""Idempotently ingest only approved BallotSense corpus records into Firestore."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from google.cloud import firestore

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from ballotsense_api.models import ReviewStatus, SourceChunk, SourceDocument


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def approved_sources(path: Path) -> list[SourceDocument]:
    records = load_json(path)
    sources = [SourceDocument.model_validate(source) for source in records["sources"]]
    if any(source.review_status != ReviewStatus.APPROVED for source in sources):
        raise ValueError("refusing to ingest a source that is not approved")
    return sources


def approved_chunks(path: Path) -> list[SourceChunk]:
    corpus = load_json(path)
    return [SourceChunk.model_validate(chunk) for chunk in corpus["chunks"]]


def write_demo_metadata(
    batch: firestore.WriteBatch,
    client: firestore.Client,
    *,
    corpus_release_id: str,
) -> None:
    batch.set(
        client.collection("elections").document("ca-scc-2026-primary"),
        {
            "id": "ca-scc-2026-primary",
            "name": "Archived June 2, 2026 Statewide Direct Primary Election",
            "election_date": "2026-06-02",
            "jurisdiction": "Santa Clara County, CA",
            "archive_demo": True,
            "corpus_release_id": corpus_release_id,
        },
    )
    batch.set(
        client.collection("jurisdictions").document("scvosa"),
        {
            "id": "scvosa",
            "name": "Santa Clara Valley Open Space Authority",
            "parent_id": "santa-clara-county",
            "type": "special_district",
        },
    )
    batch.set(
        client.collection("contests").document("scvosa-measure-d"),
        {
            "id": "scvosa-measure-d",
            "election_id": "ca-scc-2026-primary",
            "jurisdiction_id": "scvosa",
            "type": "measure",
            "title": "Measure D",
            "measure_id": "scvosa-measure-d",
            "corpus_release_id": corpus_release_id,
        },
    )
    batch.set(
        client.collection("measures").document("scvosa-measure-d"),
        {
            "id": "scvosa-measure-d",
            "contest_id": "scvosa-measure-d",
            "title": "Santa Clara Valley Open Space Authority Special Parcel Tax",
            "measure_type": "parcel_tax",
        },
    )


def ingest(project_id: str, corpus_release_id: str) -> str:
    client = firestore.Client(project=project_id)
    sources = approved_sources(ROOT / "data/source_records/measure-d.json")
    chunks = approved_chunks(ROOT / "data/corpus/measure-d-approved-chunks.json")
    source_by_id = {source.id: source for source in sources}
    if any(chunk.source_id not in source_by_id for chunk in chunks):
        raise ValueError("refusing to ingest a chunk with an unknown source")

    run_id = f"ingest-{uuid4()}"
    now = datetime.now(UTC).isoformat()
    batch = client.batch()
    write_demo_metadata(batch, client, corpus_release_id=corpus_release_id)

    for source in sources:
        record = source.model_dump(mode="json")
        record["corpus_release_id"] = corpus_release_id
        batch.set(client.collection("sources").document(source.id), record)

    for chunk in chunks:
        source = source_by_id[chunk.source_id]
        record = chunk.model_dump(mode="json")
        record.pop("embedding", None)
        record.update(
            {
                "approved_for_retrieval": True,
                "review_status": ReviewStatus.APPROVED.value,
                "source_type": source.source_type.value,
                "source_tier": source.source_tier,
                "source_published_at": source.published_at.isoformat()
                if source.published_at is not None
                else None,
                "corpus_release_id": corpus_release_id,
            }
        )
        batch.set(client.collection("source_chunks").document(chunk.id), record, merge=True)

    batch.set(
        client.collection("ingestion_runs").document(run_id),
        {
            "id": run_id,
            "started_at": now,
            "completed_at": now,
            "status": "succeeded",
            "corpus_release_id": corpus_release_id,
            "source_ids": sorted(source_by_id),
            "chunk_ids": sorted(chunk.id for chunk in chunks),
            "embedding_model": None,
            "note": "Approved corpus metadata ingested; embeddings intentionally not generated.",
        },
    )
    batch.commit()
    return run_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--corpus-release", default="measure-d-review-2026-07-12")
    args = parser.parse_args()
    print(ingest(args.project, args.corpus_release))


if __name__ == "__main__":
    main()
