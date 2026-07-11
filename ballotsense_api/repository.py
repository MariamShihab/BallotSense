"""Small stateless repository abstraction.

The in-memory implementation exists only for local contract development. The
deployment implementation will use Firestore without changing API contracts.
"""

from __future__ import annotations

from collections.abc import Iterable

from .models import SourceDocument


class SourceRepository:
    def list_sources(self, election_id: str | None = None) -> list[SourceDocument]:
        raise NotImplementedError

    def get_source(self, source_id: str) -> SourceDocument | None:
        raise NotImplementedError


class InMemorySourceRepository(SourceRepository):
    def __init__(self, sources: Iterable[SourceDocument] = ()) -> None:
        self._sources = {source.id: source for source in sources}

    def list_sources(self, election_id: str | None = None) -> list[SourceDocument]:
        sources = self._sources.values()
        if election_id is not None:
            sources = (source for source in sources if source.election_id == election_id)
        return sorted(sources, key=lambda source: source.id)

    def get_source(self, source_id: str) -> SourceDocument | None:
        return self._sources.get(source_id)
