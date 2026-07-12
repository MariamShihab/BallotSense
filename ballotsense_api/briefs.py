"""Validated contest-brief orchestration with redacted claim auditing."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from google.cloud import firestore

from .firestore_repository import FirestoreSourceRepository
from .generation import (
    EvidencePacket,
    EvidencePacketChunk,
    GeminiCitedBriefGenerator,
    InvalidBriefOutput,
    safe_insufficient_evidence_response,
    safe_not_covered_response,
)
from .models import (
    BriefRequest,
    BriefResponse,
    Citation,
    CitedClaim,
    ClaimAuditRecord,
    EvidenceFinding,
    RetrievalRequest,
)
from .repository import SourceRepository
from .retrieval import FirestoreRetriever, VertexQueryEmbedder

LENS_QUERIES: dict[str, str] = {
    "housing-affordability": (
        "What reviewed evidence relates to housing affordability or property costs?"
    ),
    "public-safety": "What reviewed evidence relates to public safety or wildfire risk?",
    "climate-environment": (
        "What does Measure D say about protecting open space and natural resources?"
    ),
    "public-education": "What reviewed evidence relates to public education or schools?",
}
CORPUS_VERSION = "measure-d-approved-corpus-v1"


class ClaimAuditRepository:
    def record(self, record: ClaimAuditRecord) -> None:
        raise NotImplementedError


class InMemoryClaimAuditRepository(ClaimAuditRepository):
    """Development-only audit store; production storage is configured separately."""

    def __init__(self) -> None:
        self.records: list[ClaimAuditRecord] = []

    def record(self, record: ClaimAuditRecord) -> None:
        self.records.append(record)


class FirestoreClaimAuditRepository(ClaimAuditRepository):
    """Durable, redacted audit storage for a configured Cloud Run deployment."""

    def __init__(self, client: firestore.Client) -> None:
        self._client = client

    def record(self, record: ClaimAuditRecord) -> None:
        self._client.collection("claim_audits").document(record.id).set(
            record.model_dump(mode="json")
        )


class BriefService:
    """Creates one safe finding per selected lens, never accepting voter data."""

    def __init__(
        self,
        retriever: FirestoreRetriever,
        source_repository: SourceRepository,
        generate: Callable[[EvidencePacket, str | None], BriefResponse],
        audit_repository: ClaimAuditRepository,
    ) -> None:
        self._retriever = retriever
        self._source_repository = source_repository
        self._generate = generate
        self._audit_repository = audit_repository

    def create(self, request: BriefRequest) -> BriefResponse:
        has_contest_corpus = any(
            source.contest_id == request.contest_id
            for source in self._source_repository.list_sources(request.election_id)
        )
        if not has_contest_corpus:
            response = safe_not_covered_response(request)
            self._audit(request, [], "not_covered")
            return response

        findings: list[EvidenceFinding] = []
        for lens_id in request.lens_ids:
            lens_request = BriefRequest(
                election_id=request.election_id,
                contest_id=request.contest_id,
                lens_ids=[lens_id],
            )
            retrieval = self._retriever.retrieve(
                RetrievalRequest(
                    election_id=request.election_id,
                    contest_id=request.contest_id,
                    lens_id=lens_id,
                    query_text=LENS_QUERIES.get(lens_id, "What reviewed evidence is available?"),
                    limit=3,
                )
            )
            if not retrieval.chunks:
                fallback = safe_insufficient_evidence_response(lens_request)
                self._audit(lens_request, [], "insufficient_evidence")
                findings.extend(fallback.findings)
                continue

            packet_chunks = []
            for chunk in retrieval.chunks:
                source = self._source_repository.get_source(chunk.source_id)
                if source is None:
                    continue
                packet_chunks.append(
                    EvidencePacketChunk.from_retrieved_chunk(chunk, str(source.canonical_url))
                )
            if not packet_chunks:
                fallback = safe_insufficient_evidence_response(lens_request)
                self._audit(lens_request, [], "missing_approved_source_metadata")
                findings.extend(fallback.findings)
                continue

            packet = EvidencePacket(request=lens_request, chunks=packet_chunks)
            try:
                generated = self._generate(packet, None)
                findings.extend(generated.findings)
                self._audit(lens_request, [chunk.chunk_id for chunk in packet_chunks], "accepted")
            except (InvalidBriefOutput, ValueError) as error:
                self._retry_or_abstain(lens_request, packet, findings, str(error))

        return BriefResponse(
            election_id=request.election_id,
            contest_id=request.contest_id,
            findings=findings,
            disclaimer="Research assistance only; BallotSense does not recommend or rank choices.",
        )

    def _audit(self, request: BriefRequest, chunk_ids: list[str], outcome: str) -> None:
        self._audit_repository.record(
            ClaimAuditRecord(
                id=str(uuid4()),
                created_at=datetime.now(UTC),
                corpus_version=CORPUS_VERSION,
                election_id=request.election_id,
                contest_id=request.contest_id,
                lens_ids=request.lens_ids,
                chunk_ids=chunk_ids,
                validator_outcome=outcome,
            )
        )

    def _retry_or_abstain(
        self,
        request: BriefRequest,
        packet: EvidencePacket,
        findings: list[EvidenceFinding],
        validator_reason: str,
    ) -> None:
        chunk_ids = [chunk.chunk_id for chunk in packet.chunks]
        try:
            generated = self._generate(
                packet,
                "The previous response was rejected because: "
                f"{validator_reason}. Return only exact citation metadata from the "
                "evidence packet and no recommendation language.",
            )
            findings.extend(generated.findings)
            self._audit(request, chunk_ids, "accepted_after_retry")
        except (InvalidBriefOutput, ValueError):
            findings.append(self._verified_excerpt(packet))
            self._audit(request, chunk_ids, "verified_excerpt_fallback")

    @staticmethod
    def _verified_excerpt(packet: EvidencePacket) -> EvidenceFinding:
        """Display an exact reviewed excerpt when generated prose is unsafe."""

        chunk = next(
            (item for item in packet.chunks if item.source_tier == 1), packet.chunks[0]
        )
        attribution = None if chunk.source_tier == 1 else f"Attributed {chunk.source_type}"
        return EvidenceFinding(
            status="supported",
            lens_id=packet.request.lens_ids[0],
            summary=CitedClaim(
                text=chunk.text,
                attribution=attribution,
                citations=[
                    Citation(
                        source_id=chunk.source_id,
                        chunk_id=chunk.chunk_id,
                        locator=chunk.locator,
                        public_source_url=chunk.public_source_url,
                        source_type=chunk.source_type,
                    )
                ],
            ),
        )


def build_firestore_brief_service(project_id: str) -> BriefService:
    """Build the production dependency graph from reviewed Firestore records."""

    client = firestore.Client(project=project_id)
    return BriefService(
        retriever=FirestoreRetriever(client, VertexQueryEmbedder(project_id)),
        source_repository=FirestoreSourceRepository(client),
        generate=GeminiCitedBriefGenerator(project_id).generate,
        audit_repository=FirestoreClaimAuditRepository(client),
    )
