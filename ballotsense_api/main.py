"""Citation-first API entry point."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from .models import SourceCatalogResponse, SourceDocument
from .repository import InMemorySourceRepository, SourceRepository

app = FastAPI(
    title="BallotSense API",
    version="0.1.0",
    description="A citation-first voter education API. Only reviewed sources may enter retrieval.",
)

# Intentionally empty: no election source enters the corpus until it has passed
# the documented review process. Replace with a Firestore repository in deploys.
repository: SourceRepository = InMemorySourceRepository()


def get_repository() -> SourceRepository:
    return repository


SourceRepositoryDependency = Annotated[SourceRepository, Depends(get_repository)]


@app.get("/healthz", tags=["operations"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/sources", response_model=SourceCatalogResponse, tags=["sources"])
def list_sources(
    source_repository: SourceRepositoryDependency,
    election_id: str | None = None,
) -> SourceCatalogResponse:
    return SourceCatalogResponse(sources=source_repository.list_sources(election_id))


@app.get("/v1/sources/{source_id}", response_model=SourceDocument, tags=["sources"])
def get_source(
    source_id: str,
    source_repository: SourceRepositoryDependency,
) -> SourceDocument:
    source = source_repository.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source
