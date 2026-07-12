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


class CorrectionIssueType(StrEnum):
    INCORRECT_SOURCE = "incorrect_source"
    MISLEADING_SUMMARY = "misleading_summary"
    BROKEN_SOURCE_LINK = "broken_source_link"
    PRIVACY_CONCERN = "privacy_concern"
    OTHER = "other"


class BallotDiscoveryStatus(StrEnum):
    REQUIRES_CONFIRMATION = "requires_confirmation"
    PROVIDER_NOT_CONFIGURED = "provider_not_configured"


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
    corpus_release_id: str | None = Field(default=None, min_length=1, max_length=160)
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


class EvidenceStatus(StrEnum):
    SUPPORTED = "supported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    PENDING_REVIEW = "pending_review"
    NOT_COVERED = "not_covered"


class RetrievedChunk(BallotSenseModel):
    """A reviewed source excerpt returned by filtered vector retrieval."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_type: SourceType
    source_tier: int = Field(ge=1, le=3)
    locator: str = Field(min_length=1, max_length=240)
    text: str = Field(min_length=1, max_length=10_000)
    distance: float = Field(ge=0)


class RetrievalRequest(BallotSenseModel):
    """Internal retrieval input; no voter profile or free-text values."""

    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    lens_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    query_text: str = Field(min_length=1, max_length=1_000)
    limit: int = Field(default=6, ge=1, le=12)


class RetrievalResult(BallotSenseModel):
    request: RetrievalRequest
    status: EvidenceStatus
    chunks: list[RetrievedChunk] = Field(default_factory=list)

    @model_validator(mode="after")
    def evidence_state_matches_chunks(self) -> RetrievalResult:
        if self.status == EvidenceStatus.SUPPORTED and not self.chunks:
            raise ValueError("supported retrieval results require chunks")
        if self.status == EvidenceStatus.INSUFFICIENT_EVIDENCE and self.chunks:
            raise ValueError("insufficient evidence results cannot carry chunks")
        return self


class Citation(BallotSenseModel):
    """A citation from a generated claim back to an approved source chunk."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    locator: str = Field(min_length=1, max_length=240)
    public_source_url: HttpUrl
    source_type: SourceType


class CitedClaim(BallotSenseModel):
    """A claim eligible for display in the voter-facing application."""

    text: str = Field(min_length=1, max_length=10_000)
    citations: list[Citation] = Field(min_length=1, max_length=4)
    attribution: str | None = Field(default=None, max_length=240)


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


class ContestSuggestion(BallotSenseModel):
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    title: str = Field(min_length=1, max_length=300)
    contest_type: ContestType
    jurisdiction: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=500)
    confidence: str = Field(pattern=r"^(manual_fallback|low|medium|high)$")


class AddressResolutionRequest(BallotSenseModel):
    """Ephemeral address lookup input.

    The raw address is accepted only to resolve contests for this one request.
    It must not be written to logs, audits, Firestore, Cloud Storage, or model
    prompts.
    """

    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    address: str = Field(min_length=5, max_length=300)


class AddressResolutionResponse(BallotSenseModel):
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    status: BallotDiscoveryStatus
    provider_name: str = Field(min_length=1, max_length=160)
    message: str = Field(min_length=1, max_length=600)
    inferred_contests: list[ContestSuggestion] = Field(default_factory=list, max_length=24)
    manual_contests: list[ContestSuggestion] = Field(default_factory=list, max_length=24)
    requires_confirmation: bool = True
    address_retained: bool = False

    @model_validator(mode="after")
    def address_is_never_retained(self) -> AddressResolutionResponse:
        if self.address_retained:
            raise ValueError("address resolution responses must not retain raw address")
        if self.status == BallotDiscoveryStatus.PROVIDER_NOT_CONFIGURED and self.inferred_contests:
            raise ValueError("unconfigured providers cannot infer contests")
        if not self.requires_confirmation:
            raise ValueError("address-discovered contests require user confirmation")
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
    findings: list[EvidenceFinding] = Field(min_length=1, max_length=4)
    disclaimer: str = Field(min_length=1, max_length=500)


class ClaimAuditRecord(BallotSenseModel):
    """Redacted operational record for a generated brief, never voter data."""

    id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    created_at: datetime
    corpus_version: str = Field(min_length=1, max_length=160)
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    lens_ids: list[str] = Field(min_length=1, max_length=4)
    chunk_ids: list[str] = Field(max_length=12)
    validator_outcome: str = Field(min_length=1, max_length=120)


class CorrectionReportRequest(BallotSenseModel):
    """User-submitted correction bound to an already displayed citation.

    This request intentionally does not accept names, email addresses, voter
    addresses, ballot choices, free-form values, local notes, or accounts.
    """

    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    lens_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    issue_type: CorrectionIssueType
    description: str = Field(min_length=10, max_length=1_000)


class CorrectionReportRecord(BallotSenseModel):
    """Redacted correction record safe for reviewer workflow storage."""

    id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    created_at: datetime
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    lens_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    issue_type: CorrectionIssueType
    redacted_description: str = Field(min_length=1, max_length=1_000)
    redaction_applied: bool
    status: ReviewStatus = ReviewStatus.PENDING


class CorrectionReportResponse(BallotSenseModel):
    report_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    status: ReviewStatus
    message: str = Field(min_length=1, max_length=240)


class SourceCatalogResponse(BallotSenseModel):
    sources: list[SourceDocument]
