"""Firestore-backed repository for approved election sources only."""

from __future__ import annotations

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from .models import ReviewStatus, SourceDocument
from .repository import SourceRepository


class FirestoreSourceRepository(SourceRepository):
    """Read only approved source records from Firestore Native mode."""

    def __init__(self, client: firestore.Client) -> None:
        self._client = client

    def list_sources(self, election_id: str | None = None) -> list[SourceDocument]:
        query = self._client.collection("sources").where(
            filter=FieldFilter("review_status", "==", ReviewStatus.APPROVED.value)
        )
        if election_id is not None:
            query = query.where(filter=FieldFilter("election_id", "==", election_id))
        return sorted(
            (SourceDocument.model_validate(snapshot.to_dict()) for snapshot in query.stream()),
            key=lambda source: source.id,
        )

    def get_source(self, source_id: str) -> SourceDocument | None:
        snapshot = self._client.collection("sources").document(source_id).get()
        if not snapshot.exists:
            return None
        source = SourceDocument.model_validate(snapshot.to_dict())
        if source.review_status != ReviewStatus.APPROVED:
            return None
        return source
