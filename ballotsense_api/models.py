"""Pydantic contracts for the reviewed election-source corpus.

These models deliberately make a citation mandatory for a generated factual
claim. Retrieval and generation layers should exchange these models rather
than unstructured dictionaries.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, model_validator


class SourceType(StrEnum):
    OFFICIAL_BALLOT = "official_ballot"
    OFFICIAL_MEASURE_TEXT = "official_measure_text"
    COUNTY_VOTER_GUIDE = "county_voter_guide"
    STATE_VOTER_GUIDE = "state_voter_guide"
    ELECTIONS_OFFICE_MATERIAL = "elections_office_material"
    FILED_CANDIDATE_STATEMENT = "filed_candidate_statement"
    CAMPAIGN_MATERIAL = "campaign_material"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SourceDocument(BaseModel):
    """A document that may be included in the retrieval corpus after review."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    title: str = Field(min_length=1, max_length=500)
    canonical_url: HttpUrl
    publisher: str = Field(min_length=1, max_length=200)
    source_type: SourceType
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    jurisdiction: str = Field(min_length=1, max_length=200)
    retrieved_at: datetime
    published_at: date | None = None
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    review_status: ReviewStatus
    reviewed_at: datetime | None = None
    reviewer: str | None = Field(default=None, min_length=1, max_length=120)

    @model_validator(mode="after")
    def approved_sources_have_a_review_time(self) -> "SourceDocument":
        if self.review_status == ReviewStatus.APPROVED and self.reviewed_at is None:
            raise ValueError("approved sources require reviewed_at")
        return self


class SourceChunk(BaseModel):
    """A retrievable, verbatim excerpt of a reviewed source document."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str | None = Field(default=None, max_length=128)
    text: str = Field(min_length=1, max_length=10_000)
    locator: str = Field(min_length=1, max_length=240)
    embedding: list[float] | None = None


class Citation(BaseModel):
    """A citation from a generated claim back to an approved source chunk."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    locator: str = Field(min_length=1, max_length=240)


class CitedClaim(BaseModel):
    """A claim eligible for display in the voter-facing application."""

    text: str = Field(min_length=1, max_length=1_500)
    citations: list[Citation] = Field(min_length=1)
    attribution: str | None = Field(default=None, max_length=240)


class SourceCatalogResponse(BaseModel):
    sources: list[SourceDocument]
