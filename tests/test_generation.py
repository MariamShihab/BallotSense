import pytest

from ballotsense_api.generation import (
    CitedBriefValidator,
    EvidencePacket,
    EvidencePacketChunk,
    InvalidBriefOutput,
    safe_insufficient_evidence_response,
)
from ballotsense_api.models import BriefRequest, BriefResponse, EvidenceFinding, EvidenceStatus


def request() -> BriefRequest:
    return BriefRequest(
        election_id="ca-scc-2026-primary",
        contest_id="scvosa-measure-d",
        lens_ids=["climate-environment"],
    )


def packet() -> EvidencePacket:
    return EvidencePacket(
        request=request(),
        chunks=[
            EvidencePacketChunk(
                source_id="scvosa-measure-d-impartial-analysis",
                chunk_id="scvosa-measure-d-analysis-tax",
                election_id="ca-scc-2026-primary",
                contest_id="scvosa-measure-d",
                source_type="elections_office_material",
                source_tier=1,
                locator="PDF p. 1, tax paragraph",
                public_source_url="https://example.gov/measure-d-analysis.pdf",
                text="The measure would authorize a special parcel tax.",
            )
        ],
    )


def response(
    citation: dict[str, str] | None = None,
    text: str = "The analysis describes a special parcel tax.",
) -> BriefResponse:
    citation = citation or {
        "source_id": "scvosa-measure-d-impartial-analysis",
        "chunk_id": "scvosa-measure-d-analysis-tax",
        "locator": "PDF p. 1, tax paragraph",
        "public_source_url": "https://example.gov/measure-d-analysis.pdf",
        "source_type": "elections_office_material",
    }
    return BriefResponse(
        election_id="ca-scc-2026-primary",
        contest_id="scvosa-measure-d",
        findings=[
            EvidenceFinding(
                status=EvidenceStatus.SUPPORTED,
                lens_id="climate-environment",
                summary={"text": text, "citations": [citation]},
            )
        ],
        disclaimer="Research assistance only; not a voting recommendation.",
    )


def test_validator_accepts_exact_evidence_citation() -> None:
    assert CitedBriefValidator().validate(response(), packet()).findings[0].status == "supported"


def test_validator_rejects_fabricated_citation() -> None:
    with pytest.raises(InvalidBriefOutput, match="does not reference"):
        CitedBriefValidator().validate(
            response(citation={
                "source_id": "scvosa-measure-d-impartial-analysis",
                "chunk_id": "invented-chunk",
                "locator": "PDF p. 1, tax paragraph",
                "public_source_url": "https://example.gov/measure-d-analysis.pdf",
                "source_type": "elections_office_material",
            }),
            packet(),
        )


def test_validator_rejects_wrong_contest_packet() -> None:
    wrong_packet = packet().model_copy(
        update={"request": request().model_copy(update={"contest_id": "scc-bos-district-1"})}
    )
    with pytest.raises(InvalidBriefOutput, match="contest"):
        CitedBriefValidator().validate(response(), wrong_packet)


def test_validator_rejects_recommendation_language() -> None:
    with pytest.raises(InvalidBriefOutput, match="prohibited"):
        CitedBriefValidator().validate(
            response(text="Voters should vote yes on Measure D."), packet()
        )


def test_safe_fallback_has_no_factual_summary() -> None:
    fallback = safe_insufficient_evidence_response(request())
    assert fallback.findings[0].status == "insufficient_evidence"
    assert fallback.findings[0].summary is None
