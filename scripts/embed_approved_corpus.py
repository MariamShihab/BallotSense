"""Embed only approved Firestore chunks with the locked Vertex AI contract."""

from __future__ import annotations

import argparse
import os
from datetime import UTC, datetime
from uuid import uuid4

from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.vector import Vector
from google.genai import types

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768
VERTEX_LOCATION = "global"
CORPUS_RELEASE_ID = "measure-d-review-2026-07-12"


def embedding_client(project_id: str) -> genai.Client:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = VERTEX_LOCATION
    return genai.Client()


def document_embedding(client: genai.Client, text: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIMENSION,
            auto_truncate=False,
        ),
    )
    if len(response.embeddings) != 1:
        raise ValueError("expected exactly one embedding response")
    values = list(response.embeddings[0].values)
    if len(values) != EMBEDDING_DIMENSION:
        raise ValueError(f"expected {EMBEDDING_DIMENSION} dimensions, got {len(values)}")
    return values


def embed(project_id: str) -> str:
    firestore_client = firestore.Client(project=project_id)
    vertex_client = embedding_client(project_id)
    query = (
        firestore_client.collection("source_chunks")
        .where(filter=FieldFilter("review_status", "==", "approved"))
        .where(filter=FieldFilter("approved_for_retrieval", "==", True))
    )
    snapshots = list(query.stream())
    run_id = f"embed-{uuid4()}"
    batch = firestore_client.batch()
    chunk_ids: list[str] = []
    for snapshot in snapshots:
        record = snapshot.to_dict()
        if (
            record.get("embedding") is not None
            and record.get("embedding_model") == EMBEDDING_MODEL
            and record.get("embedding_dimension") == EMBEDDING_DIMENSION
            and record.get("embedding_task_type") == "RETRIEVAL_DOCUMENT"
        ):
            continue
        embedding = document_embedding(vertex_client, record["text"])
        batch.update(
            snapshot.reference,
            {
                "embedding": Vector(embedding),
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dimension": EMBEDDING_DIMENSION,
                "embedding_task_type": "RETRIEVAL_DOCUMENT",
                "embedded_at": datetime.now(UTC).isoformat(),
            },
        )
        chunk_ids.append(snapshot.id)
    completed_at = datetime.now(UTC).isoformat()
    batch.set(
        firestore_client.collection("ingestion_runs").document(run_id),
        {
            "id": run_id,
            "started_at": completed_at,
            "completed_at": completed_at,
            "status": "succeeded",
            "corpus_release_id": CORPUS_RELEASE_ID,
            "chunk_ids": sorted(chunk_ids),
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "embedding_task_type": "RETRIEVAL_DOCUMENT",
        },
    )
    batch.commit()
    return run_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    print(embed(args.project))


if __name__ == "__main__":
    main()
