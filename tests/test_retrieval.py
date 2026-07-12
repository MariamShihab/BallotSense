from __future__ import annotations

import pytest

from ballotsense_api.models import EvidenceStatus, RetrievalRequest
from ballotsense_api.retrieval import FirestoreRetriever


class FakeSnapshot:
    def __init__(self, document_id: str, data: dict[str, object]) -> None:
        self.id = document_id
        self._data = data

    def to_dict(self) -> dict[str, object]:
        return self._data


class FakeQuery:
    def __init__(self, snapshots: list[FakeSnapshot]) -> None:
        self.snapshots = snapshots
        self.filters: list[object] = []
        self.nearest_kwargs: dict[str, object] = {}

    def where(self, *, filter: object) -> FakeQuery:
        self.filters.append(filter)
        return self

    def find_nearest(self, **kwargs: object) -> FakeQuery:
        self.nearest_kwargs = kwargs
        return self

    def stream(self) -> list[FakeSnapshot]:
        return self.snapshots


class FakeClient:
    def __init__(self, query: FakeQuery) -> None:
        self.query = query

    def collection(self, _: str) -> FakeQuery:
        return self.query


def request(contest_id: str = "scvosa-measure-d") -> RetrievalRequest:
    return RetrievalRequest(
        election_id="ca-scc-2026-primary",
        contest_id=contest_id,
        lens_id="climate-environment",
        query_text="open space and wildfire",
    )


def approved_snapshot() -> FakeSnapshot:
    return FakeSnapshot(
        "scvosa-measure-d-analysis-tax",
        {
            "source_id": "scvosa-measure-d-impartial-analysis",
            "election_id": "ca-scc-2026-primary",
            "contest_id": "scvosa-measure-d",
            "source_type": "elections_office_material",
            "source_tier": 1,
            "locator": "PDF p. 1",
            "text": "A reviewed source excerpt.",
            "cosine_distance": 0.12,
            "embedding_model": "gemini-embedding-001",
            "embedding_dimension": 768,
        },
    )


def test_retrieval_returns_provenance_after_hard_filters() -> None:
    query = FakeQuery([approved_snapshot()])
    retriever = FirestoreRetriever(FakeClient(query), lambda _: [0.0] * 768)  # type: ignore[arg-type]

    result = retriever.retrieve(request())

    assert result.status == EvidenceStatus.SUPPORTED
    assert result.chunks[0].source_id == "scvosa-measure-d-impartial-analysis"
    assert result.chunks[0].locator == "PDF p. 1"
    assert len(query.filters) == 4
    assert query.nearest_kwargs["limit"] == 6


def test_retrieval_abstains_when_no_chunk_matches_contest() -> None:
    query = FakeQuery([])
    retriever = FirestoreRetriever(FakeClient(query), lambda _: [0.0] * 768)  # type: ignore[arg-type]

    result = retriever.retrieve(request("scc-bos-district-1"))

    assert result.status == EvidenceStatus.INSUFFICIENT_EVIDENCE
    assert result.chunks == []


def test_retrieval_rejects_wrong_dimension_query_vector() -> None:
    retriever = FirestoreRetriever(FakeClient(FakeQuery([])), lambda _: [0.0] * 767)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="expected 768 dimensions"):
        retriever.retrieve(request())
