from fastapi.testclient import TestClient

from ballotsense_api.corrections import CorrectionService, InMemoryCorrectionReportRepository
from ballotsense_api.main import app, get_correction_service
from ballotsense_api.models import CorrectionReportRequest


def correction_payload(
    description: str = "Please check whether this summary matches the source.",
) -> dict[str, str]:
    return {
        "election_id": "ca-scc-2026-primary",
        "contest_id": "scvosa-measure-d",
        "lens_id": "climate-environment",
        "source_id": "scvosa-measure-d-impartial-analysis",
        "chunk_id": "scvosa-measure-d-analysis-accountability",
        "issue_type": "misleading_summary",
        "description": description,
    }


def test_correction_service_redacts_obvious_personal_data() -> None:
    repository = InMemoryCorrectionReportRepository()
    service = CorrectionService(repository)

    response = service.submit(
        CorrectionReportRequest.model_validate(
            correction_payload(
            "Email me at voter@example.com or call 408-555-1212. "
            "I will vote yes, but the source wording seems off."
            )
        )
    )

    record = repository.records[0]
    assert response.status == "pending"
    assert record.redaction_applied is True
    assert "voter@example.com" not in record.redacted_description
    assert "408-555-1212" not in record.redacted_description
    assert "I will vote yes" not in record.redacted_description
    assert "[redacted-email]" in record.redacted_description
    assert "[redacted-phone]" in record.redacted_description
    assert "[redacted-vote-preference]" in record.redacted_description
    assert not hasattr(record, "description")
    assert not hasattr(record, "local_note")


def test_correction_endpoint_uses_redacted_repository() -> None:
    repository = InMemoryCorrectionReportRepository()
    service = CorrectionService(repository)
    app.dependency_overrides[get_correction_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/v1/corrections",
            json=correction_payload("The source link and claim should be reviewed."),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert len(repository.records) == 1
    assert repository.records[0].source_id == "scvosa-measure-d-impartial-analysis"


def test_correction_endpoint_rejects_extra_voter_data() -> None:
    repository = InMemoryCorrectionReportRepository()
    service = CorrectionService(repository)
    payload = correction_payload("The source link and claim should be reviewed.")
    payload["vote_choice"] = "yes"
    payload["local_note"] = "private browser note"

    app.dependency_overrides[get_correction_service] = lambda: service
    try:
        response = TestClient(app).post("/v1/corrections", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert repository.records == []
