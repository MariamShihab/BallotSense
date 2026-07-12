"""Filtered native Firestore cosine retrieval over approved corpus chunks."""

from __future__ import annotations

import os
from collections.abc import Callable

from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.genai import types

from .models import EvidenceStatus, RetrievalRequest, RetrievalResult, RetrievedChunk, SourceType

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


class VertexQueryEmbedder:
    """Create a locked-dimension Vertex query embedding for retrieval only."""

    def __init__(self, project_id: str, location: str = "global") -> None:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = location
        self._client = genai.Client()

    def __call__(self, text: str) -> list[float]:
        response = self._client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=EMBEDDING_DIMENSION,
                auto_truncate=False,
            ),
        )
        if len(response.embeddings) != 1:
            raise ValueError("expected exactly one query embedding")
        values = list(response.embeddings[0].values)
        if len(values) != EMBEDDING_DIMENSION:
            raise ValueError(f"expected {EMBEDDING_DIMENSION} dimensions, got {len(values)}")
        return values


class FirestoreRetriever:
    """Return only approved chunks bound to the requested election and contest."""

    def __init__(
        self,
        client: firestore.Client,
        query_embedder: Callable[[str], list[float]],
    ) -> None:
        self._client = client
        self._query_embedder = query_embedder

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        query_vector = self._query_embedder(request.query_text)
        if len(query_vector) != EMBEDDING_DIMENSION:
            raise ValueError(f"expected {EMBEDDING_DIMENSION} dimensions, got {len(query_vector)}")

        query = (
            self._client.collection("source_chunks")
            .where(filter=FieldFilter("review_status", "==", "approved"))
            .where(filter=FieldFilter("approved_for_retrieval", "==", True))
            .where(filter=FieldFilter("election_id", "==", request.election_id))
            .where(filter=FieldFilter("contest_id", "==", request.contest_id))
            .find_nearest(
                vector_field="embedding",
                query_vector=query_vector,
                limit=request.limit,
                distance_measure=DistanceMeasure.COSINE,
                distance_result_field="cosine_distance",
            )
        )
        chunks = [
            RetrievedChunk(
                source_id=record["source_id"],
                chunk_id=snapshot.id,
                election_id=record["election_id"],
                contest_id=record["contest_id"],
                source_type=SourceType(record["source_type"]),
                source_tier=record["source_tier"],
                locator=record["locator"],
                text=record["text"],
                distance=record["cosine_distance"],
            )
            for snapshot in query.stream()
            if (record := snapshot.to_dict())["embedding_model"] == EMBEDDING_MODEL
            and record["embedding_dimension"] == EMBEDDING_DIMENSION
        ]
        if not chunks:
            return RetrievalResult(request=request, status=EvidenceStatus.INSUFFICIENT_EVIDENCE)
        return RetrievalResult(request=request, status=EvidenceStatus.SUPPORTED, chunks=chunks)
