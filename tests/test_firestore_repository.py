from __future__ import annotations

from datetime import UTC, datetime

from ballotsense_api.firestore_repository import FirestoreSourceRepository
from ballotsense_api.models import ReviewStatus, SourceDocument, SourceType


class FakeSnapshot:
    def __init__(self, data: dict[str, object], exists: bool = True) -> None:
        self._data = data
        self.exists = exists

    def to_dict(self) -> dict[str, object]:
        return self._data


class FakeDocument:
    def __init__(self, snapshot: FakeSnapshot) -> None:
        self._snapshot = snapshot

    def get(self) -> FakeSnapshot:
        return self._snapshot


class FakeQuery:
    def __init__(self, snapshots: list[FakeSnapshot]) -> None:
        self.snapshots = snapshots
        self.filters: list[object] = []

    def where(self, *, filter: object) -> FakeQuery:
        self.filters.append(filter)
        return self

    def stream(self) -> list[FakeSnapshot]:
        return self.snapshots


class FakeCollection(FakeQuery):
    def __init__(self, snapshots: list[FakeSnapshot], document: FakeDocument) -> None:
        super().__init__(snapshots)
        self._document = document

    def document(self, _: str) -> FakeDocument:
        return self._document


class FakeClient:
    def __init__(self, collection: FakeCollection) -> None:
        self._collection = collection

    def collection(self, _: str) -> FakeCollection:
        return self._collection


def approved_source(source_id: str = "measure-d-source") -> SourceDocument:
    return SourceDocument(
        id=source_id,
        title="Example official source",
        canonical_url="https://example.gov/source.pdf",
        publisher="Example County",
        source_type=SourceType.ELECTIONS_OFFICE_MATERIAL,
        source_tier=1,
        election_id="ca-scc-2026-primary",
        jurisdiction="Example County, CA",
        contest_id="measure-d",
        retrieved_at=datetime.now(UTC),
        content_sha256="a" * 64,
        snapshot_uri="gs://ballotsense-mvp-source-snapshots/example/source.pdf",
        review_status=ReviewStatus.APPROVED,
        reviewed_at=datetime.now(UTC),
        reviewer="Project owner",
    )


def test_firestore_repository_only_queries_approved_sources() -> None:
    source = approved_source()
    snapshot = FakeSnapshot(source.model_dump(mode="json"))
    collection = FakeCollection([snapshot], FakeDocument(snapshot))
    repository = FirestoreSourceRepository(FakeClient(collection))  # type: ignore[arg-type]

    assert repository.list_sources("ca-scc-2026-primary") == [source]
    assert len(collection.filters) == 2
    assert repository.get_source(source.id) == source


def test_firestore_repository_hides_non_approved_source_by_id() -> None:
    source = approved_source()
    rejected = source.model_copy(update={"review_status": ReviewStatus.REJECTED})
    snapshot = FakeSnapshot(rejected.model_dump(mode="json"))
    collection = FakeCollection([], FakeDocument(snapshot))
    repository = FirestoreSourceRepository(FakeClient(collection))  # type: ignore[arg-type]

    assert repository.get_source(source.id) is None
