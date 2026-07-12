"""Citation-first API entry point."""

import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from .ballot_discovery import AddressResolver, ProviderNotConfiguredAddressResolver
from .briefs import BriefService, build_firestore_brief_service
from .corrections import CorrectionService, build_firestore_correction_service
from .models import (
    AddressResolutionRequest,
    AddressResolutionResponse,
    BriefRequest,
    BriefResponse,
    CorrectionReportRequest,
    CorrectionReportResponse,
    SourceCatalogResponse,
    SourceDocument,
)
from .repository import InMemorySourceRepository, SourceRepository

app = FastAPI(
    title="BallotSense API",
    version="0.1.0",
    description="A citation-first voter education API. Only reviewed sources may enter retrieval.",
)

# Intentionally empty: no election source enters the corpus until it has passed
# the documented review process. Replace with a Firestore repository in deploys.
repository: SourceRepository = InMemorySourceRepository()
# Deliberately unconfigured by default: a deploy must inject reviewed Firestore
# retrieval, source metadata, Gemini generation, and a redacted audit store.
brief_service: BriefService | None = None
correction_service: CorrectionService | None = None
address_resolver: AddressResolver = ProviderNotConfiguredAddressResolver()


def get_repository() -> SourceRepository:
    return repository


SourceRepositoryDependency = Annotated[SourceRepository, Depends(get_repository)]


def get_brief_service() -> BriefService:
    if brief_service is not None:
        return brief_service
    project_id = os.environ.get("BALLOTSENSE_GCP_PROJECT")
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cited brief generation is not configured.",
        )
    return build_firestore_brief_service(project_id)


BriefServiceDependency = Annotated[BriefService, Depends(get_brief_service)]


def get_correction_service() -> CorrectionService:
    if correction_service is not None:
        return correction_service
    project_id = os.environ.get("BALLOTSENSE_GCP_PROJECT")
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Correction reporting is not configured.",
        )
    return build_firestore_correction_service(project_id)


CorrectionServiceDependency = Annotated[CorrectionService, Depends(get_correction_service)]


def get_address_resolver() -> AddressResolver:
    return address_resolver


AddressResolverDependency = Annotated[AddressResolver, Depends(get_address_resolver)]


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


@app.post("/v1/briefs", response_model=BriefResponse, tags=["briefs"])
def create_brief(
    request: BriefRequest,
    service: BriefServiceDependency,
) -> BriefResponse:
    """Return a cited brief or an explicit evidence-gap state for each lens."""
    return service.create(request)


@app.post("/v1/corrections", response_model=CorrectionReportResponse, tags=["corrections"])
def create_correction_report(
    request: CorrectionReportRequest,
    service: CorrectionServiceDependency,
) -> CorrectionReportResponse:
    """Store a redacted correction report bound to a displayed citation."""
    return service.submit(request)


@app.post("/v1/ballots/resolve-address", response_model=AddressResolutionResponse, tags=["ballots"])
def resolve_address(
    request: AddressResolutionRequest,
    resolver: AddressResolverDependency,
) -> AddressResolutionResponse:
    """Resolve an address for this request only; never store raw address."""
    return resolver.resolve(request)
