"""Pydantic contracts for the reviewed election-source corpus.

These models deliberately make a citation mandatory for a generated factual
claim. Retrieval and generation layers should exchange these models rather
than unstructured dictionaries.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class BallotSenseModel(BaseModel):
    """Strict base model for public API contracts."""

    model_config = ConfigDict(extra="forbid")


class SourceType(StrEnum):
    OFFICIAL_BALLOT = "official_ballot"
    OFFICIAL_MEASURE_TEXT = "official_measure_text"
    COUNTY_VOTER_GUIDE = "county_voter_guide"
    STATE_VOTER_GUIDE = "state_voter_guide"
    ELECTIONS_OFFICE_MATERIAL = "elections_office_material"
    FILED_CANDIDATE_STATEMENT = "filed_candidate_statement"
    BALLOT_ARGUMENT = "ballot_argument"
    CAMPAIGN_MATERIAL = "campaign_material"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SourceCandidateStatus(StrEnum):
    """A discovered source that is not yet eligible for corpus ingestion."""

    CANDIDATE = "candidate"
    FETCHED = "fetched"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class SourceDocument(BallotSenseModel):
    """A document that may be included in the retrieval corpus after review."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    title: str = Field(min_length=1, max_length=500)
    canonical_url: HttpUrl
    publisher: str = Field(min_length=1, max_length=200)
    source_type: SourceType
    source_tier: int = Field(ge=1, le=3)
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    jurisdiction: str = Field(min_length=1, max_length=200)
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    retrieved_at: datetime
    published_at: date | None = None
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    snapshot_uri: str = Field(pattern=r"^gs://[a-z0-9][a-z0-9._-]{1,220}/.+$")
    review_status: ReviewStatus
    reviewed_at: datetime | None = None
    reviewer: str | None = Field(default=None, min_length=1, max_length=120)

    @model_validator(mode="after")
    def approved_sources_have_a_review_time(self) -> SourceDocument:
        if self.review_status == ReviewStatus.APPROVED and self.reviewed_at is None:
            raise ValueError("approved sources require reviewed_at")
        return self


class SourceCandidate(BallotSenseModel):
    """Review-queue metadata kept separate from an approved source document.

    Source candidates intentionally have no content hash or chunk text. They
    cannot be passed to retrieval until a reviewer approves a fetched snapshot
    and creates a ``SourceDocument`` record.
    """

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    title: str = Field(min_length=1, max_length=500)
    canonical_url: HttpUrl
    publisher: str = Field(min_length=1, max_length=200)
    expected_source_type: SourceType
    source_tier: int = Field(ge=1, le=3)
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    jurisdiction: str = Field(min_length=1, max_length=200)
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    document_role: str = Field(min_length=1, max_length=120)
    artifact_kind: str = Field(min_length=1, max_length=80)
    has_stable_locator: bool
    inclusion_reason: str = Field(min_length=1, max_length=1_000)
    attribution_note: str = Field(min_length=1, max_length=1_000)
    retrieved_at: datetime
    published_at: date | None = None
    status: SourceCandidateStatus = SourceCandidateStatus.CANDIDATE
    reviewer: str = Field(min_length=1, max_length=120)
    review_note: str | None = Field(default=None, max_length=1_000)


class ExtractionStatus(StrEnum):
    """Quality state for a review-only, non-retrievable extracted excerpt."""

    READY_FOR_REVIEW = "ready_for_review"
    NEEDS_REVIEWER_COMPARISON = "needs_reviewer_comparison"


class SourceChunkCandidate(BallotSenseModel):
    """A verbatim extraction awaiting human review, never a retrievable chunk."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    text: str = Field(min_length=1, max_length=10_000)
    locator: str = Field(min_length=1, max_length=240)
    extraction_method: str = Field(min_length=1, max_length=120)
    extraction_status: ExtractionStatus
    reviewer_note: str | None = Field(default=None, max_length=1_000)


class SourceChunk(BallotSenseModel):
    """A retrievable, verbatim excerpt of a reviewed source document."""

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str | None = Field(default=None, max_length=128)
    text: str = Field(min_length=1, max_length=10_000)
    locator: str = Field(min_length=1, max_length=240)
    reviewed_at: datetime
    reviewer: str = Field(min_length=1, max_length=120)
    embedding: list[float] | None = None


class Citation(BallotSenseModel):
    """A citation from a generated claim back to an approved source chunk."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    locator: str = Field(min_length=1, max_length=240)


class CitedClaim(BallotSenseModel):
    """A claim eligible for display in the voter-facing application."""

    text: str = Field(min_length=1, max_length=1_500)
    citations: list[Citation] = Field(min_length=1)
    attribution: str | None = Field(default=None, max_length=240)


class EvidenceStatus(StrEnum):
    SUPPORTED = "supported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    PENDING_REVIEW = "pending_review"
    NOT_COVERED = "not_covered"


class ContestType(StrEnum):
    MEASURE = "measure"
    CANDIDATE_RACE = "candidate_race"


class Election(BallotSenseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    name: str = Field(min_length=1, max_length=240)
    election_date: date
    jurisdiction: str = Field(min_length=1, max_length=200)
    archive_demo: bool = True


class Candidate(BallotSenseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    name: str = Field(min_length=1, max_length=200)
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    party_preference: str | None = Field(default=None, max_length=120)


class Measure(BallotSenseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    title: str = Field(min_length=1, max_length=300)
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    jurisdiction: str = Field(min_length=1, max_length=200)
    ballot_question: str | None = Field(default=None, max_length=2_000)


class Contest(BallotSenseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    title: str = Field(min_length=1, max_length=300)
    contest_type: ContestType
    jurisdiction: str = Field(min_length=1, max_length=200)
    candidates: list[Candidate] = Field(default_factory=list)
    measure: Measure | None = None

    @model_validator(mode="after")
    def contest_shape_matches_type(self) -> Contest:
        if self.contest_type == ContestType.MEASURE and self.measure is None:
            raise ValueError("measure contests require a measure")
        if self.contest_type == ContestType.CANDIDATE_RACE and not self.candidates:
            raise ValueError("candidate races require candidates")
        return self


class IssueLens(BallotSenseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=600)
    retrieval_terms: list[str] = Field(min_length=1, max_length=24)
    limits: str = Field(min_length=1, max_length=600)


class EvidenceFinding(BallotSenseModel):
    status: EvidenceStatus
    lens_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    summary: CitedClaim | None = None
    explanation: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def supported_findings_require_claims(self) -> EvidenceFinding:
        if self.status == EvidenceStatus.SUPPORTED and self.summary is None:
            raise ValueError("supported findings require a cited summary")
        if self.status != EvidenceStatus.SUPPORTED and self.summary is not None:
            raise ValueError("unsupported findings cannot carry a factual claim")
        return self


class BriefRequest(BallotSenseModel):
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    lens_ids: list[str] = Field(min_length=1, max_length=4)


class BriefResponse(BallotSenseModel):
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    findings: list[EvidenceFinding] = Field(min_length=1)
    disclaimer: str = Field(min_length=1, max_length=500)


class CorrectionReport(BallotSenseModel):
    source_id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    description: str = Field(min_length=20, max_length=2_000)
    submitted_at: datetime
    status: ReviewStatus = ReviewStatus.PENDING


class SourceCatalogResponse(BallotSenseModel):
    sources: list[SourceDocument]
