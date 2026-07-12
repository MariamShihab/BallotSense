from datetime import UTC, datetime

from fastapi.testclient import TestClient

from ballotsense_api.briefs import BriefService, InMemoryClaimAuditRepository
from ballotsense_api.main import app, get_brief_service
from ballotsense_api.models import (
    BriefRequest,
    BriefResponse,
    EvidenceStatus,
    RetrievalResult,
    ReviewStatus,
    SourceDocument,
    SourceType,
)
from ballotsense_api.repository import InMemorySourceRepository


class EmptyRetriever:
    def retrieve(self, request: object) -> RetrievalResult:
        return RetrievalResult.model_validate(
            {
                "request": {
                    "election_id": "ca-scc-2026-primary",
                    "contest_id": "scvosa-measure-d",
                    "lens_id": "public-education",
                    "query_text": "No evidence",
                },
                "status": "insufficient_evidence",
            }
        )


def measure_d_source() -> SourceDocument:
    return SourceDocument(
        id="scvosa-measure-d-impartial-analysis",
        title="Measure D Impartial Analysis",
        canonical_url="https://example.gov/measure-d.pdf",
        publisher="Santa Clara County",
        source_type=SourceType.ELECTIONS_OFFICE_MATERIAL,
        source_tier=1,
        election_id="ca-scc-2026-primary",
        jurisdiction="Santa Clara County, CA",
        contest_id="scvosa-measure-d",
        retrieved_at=datetime.now(UTC),
        content_sha256="a" * 64,
        snapshot_uri="gs://ballotsense-mvp-source-snapshots/measure-d.pdf",
        review_status=ReviewStatus.APPROVED,
        reviewed_at=datetime.now(UTC),
    )


def test_brief_service_audits_an_evidence_gap_without_user_data() -> None:
    audits = InMemoryClaimAuditRepository()
    service = BriefService(
        EmptyRetriever(),  # type: ignore[arg-type]
        InMemorySourceRepository([measure_d_source()]),
        lambda _, __: (_ for _ in ()).throw(AssertionError("generation should not run")),
        audits,
    )

    response = service.create(
        BriefRequest(
            election_id="ca-scc-2026-primary",
            contest_id="scvosa-measure-d",
            lens_ids=["public-education"],
        )
    )

    assert response.findings[0].status == EvidenceStatus.INSUFFICIENT_EVIDENCE
    assert audits.records[0].validator_outcome == "insufficient_evidence"
    assert audits.records[0].chunk_ids == []
    assert not hasattr(audits.records[0], "query_text")


def test_brief_service_marks_an_uningested_contest_not_covered() -> None:
    audits = InMemoryClaimAuditRepository()
    service = BriefService(
        EmptyRetriever(),  # type: ignore[arg-type]
        InMemorySourceRepository([measure_d_source()]),
        lambda _, __: (_ for _ in ()).throw(AssertionError("generation should not run")),
        audits,
    )

    response = service.create(
        BriefRequest(
            election_id="ca-scc-2026-primary",
            contest_id="scc-bos-district-1",
            lens_ids=["climate-environment"],
        )
    )

    assert response.findings[0].status == EvidenceStatus.NOT_COVERED
    assert audits.records[0].validator_outcome == "not_covered"


class FakeBriefService:
    def create(self, request: BriefRequest) -> BriefResponse:
        return BriefResponse(
            election_id=request.election_id,
            contest_id=request.contest_id,
            findings=[
                {
                    "status": "insufficient_evidence",
                    "lens_id": request.lens_ids[0],
                    "explanation": "No reviewed evidence is available.",
                }
            ],
            disclaimer="Research assistance only; not a voting recommendation.",
        )


def test_brief_endpoint_uses_only_the_strict_brief_request() -> None:
    app.dependency_overrides[get_brief_service] = lambda: FakeBriefService()
    try:
        response = TestClient(app).post(
            "/v1/briefs",
            json={
                "election_id": "ca-scc-2026-primary",
                "contest_id": "scvosa-measure-d",
                "lens_ids": ["public-education"],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["findings"][0]["status"] == "insufficient_evidence"
