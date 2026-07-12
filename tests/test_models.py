import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from ballotsense_api.models import (
    BriefResponse,
    Candidate,
    CitedClaim,
    Contest,
    ContestType,
    CorrectionReport,
    Election,
    EvidenceFinding,
    EvidenceStatus,
    IssueLens,
    Measure,
    ReviewStatus,
    SourceCandidate,
    SourceChunk,
    SourceChunkCandidate,
    SourceDocument,
    SourceType,
)


def test_approved_source_requires_review_timestamp() -> None:
    with pytest.raises(ValidationError, match="approved sources require reviewed_at"):
        SourceDocument(
            id="ca-primary-guide",
            title="Example guide",
            canonical_url="https://example.gov/guide.pdf",
            publisher="Example County",
            source_type=SourceType.COUNTY_VOTER_GUIDE,
            source_tier=1,
            election_id="ca-2026-primary",
            jurisdiction="Example County, CA",
            contest_id="measure-d",
            retrieved_at=datetime.now(UTC),
            content_sha256="a" * 64,
            snapshot_uri="gs://ballotsense-mvp-source-snapshots/example/guide.pdf",
            review_status=ReviewStatus.APPROVED,
        )


def test_displayable_claim_requires_citation() -> None:
    with pytest.raises(ValidationError):
        CitedClaim(text="A statement without evidence.", citations=[])


def test_source_candidate_is_not_an_approved_source_document() -> None:
    candidate = SourceCandidate(
        id="measure-d-analysis",
        title="Measure D Impartial Analysis",
        canonical_url="https://example.gov/measure-d-analysis.pdf",
        publisher="Example County",
        expected_source_type=SourceType.ELECTIONS_OFFICE_MATERIAL,
        source_tier=1,
        election_id="ca-2026-primary",
        jurisdiction="Example County, CA",
        contest_id="measure-d",
        document_role="impartial analysis",
        artifact_kind="PDF",
        has_stable_locator=True,
        inclusion_reason="Official explanation of the measure.",
        attribution_note="May support factual measure explanation after review.",
        retrieved_at=datetime.now(UTC),
        reviewer="Project owner",
    )

    assert candidate.status == "candidate"
    assert not hasattr(candidate, "content_sha256")


def test_measure_d_review_queue_matches_source_candidate_contract() -> None:
    inventory_path = Path(__file__).parents[1] / "data/source_candidates/measure-d.json"
    inventory = json.loads(inventory_path.read_text())

    sources = [SourceCandidate.model_validate(source) for source in inventory["sources"]]

    assert len(sources) == 5
    assert [source.status for source in sources] == [
        "candidate",
        "approved",
        "approved",
        "approved",
        "approved",
    ]
    assert {source.expected_source_type for source in sources} == {
        SourceType.ELECTIONS_OFFICE_MATERIAL,
        SourceType.BALLOT_ARGUMENT,
    }


def test_pending_chunk_candidate_cannot_be_used_as_retrievable_chunk() -> None:
    candidate = SourceChunkCandidate(
        id="measure-d-analysis-p1-tax",
        source_id="scvosa-measure-d-impartial-analysis",
        election_id="ca-scc-2026-primary",
        contest_id="scvosa-measure-d",
        text="A source excerpt awaiting review.",
        locator="PDF p. 1",
        extraction_method="OCR from rendered source page",
        extraction_status="needs_reviewer_comparison",
    )

    assert not hasattr(candidate, "embedding")


def test_measure_d_pending_records_and_review_packet_match_contracts() -> None:
    data_root = Path(__file__).parents[1] / "data"
    source_records = json.loads((data_root / "source_records/measure-d.json").read_text())
    review_packet = json.loads((data_root / "review_packets/measure-d.json").read_text())

    sources = [SourceDocument.model_validate(source) for source in source_records["sources"]]
    chunks = [SourceChunkCandidate.model_validate(chunk) for chunk in review_packet["chunks"]]

    assert len(sources) == 4
    assert all(source.review_status == ReviewStatus.APPROVED for source in sources)
    assert all(
        source.snapshot_uri.startswith("gs://ballotsense-mvp-source-snapshots/")
        for source in sources
    )
    assert len(chunks) == 6


def test_measure_d_approved_corpus_contains_only_reviewed_chunks() -> None:
    corpus_path = Path(__file__).parents[1] / "data/corpus/measure-d-approved-chunks.json"
    corpus = json.loads(corpus_path.read_text())
    chunks = [SourceChunk.model_validate(chunk) for chunk in corpus["chunks"]]

    assert len(chunks) == 6
    assert all(chunk.reviewer == "Project owner (user)" for chunk in chunks)
    assert all(chunk.embedding is None for chunk in chunks)


def test_phase_two_coverage_and_retrieval_fixtures_include_abstention() -> None:
    data_root = Path(__file__).parents[1] / "data"
    coverage = json.loads((data_root / "coverage/measure-d-phase-2.json").read_text())
    fixtures = json.loads((data_root / "fixtures/retrieval-scenarios.json").read_text())

    measure = next(
        contest
        for contest in coverage["contests"]
        if contest["contest_id"] == "scvosa-measure-d"
    )
    education = next(
        lens for lens in measure["issue_lenses"] if lens["lens_id"] == "public-education"
    )
    expected_outcomes = {scenario["expected"] for scenario in fixtures["scenarios"]}

    assert education["deliberate_evidence_gap"] is True
    assert education["coverage"] == "none"
    assert {
        "eligible",
        "exclude_wrong_contest",
        "exclude_rejected_source",
        "insufficient_evidence",
    } <= expected_outcomes


def test_phase_one_domain_contracts_accept_the_demo_shape() -> None:
    election = Election(
        id="ca-2026-primary",
        name="Santa Clara County Primary Election",
        election_date="2026-06-02",
        jurisdiction="Santa Clara County, CA",
    )
    measure = Measure(
        id="measure-d",
        title="Santa Clara Valley Open Space Authority Special Parcel Tax",
        contest_id="measure-d",
        jurisdiction="Santa Clara County, CA",
    )
    contest = Contest(
        id="measure-d",
        election_id=election.id,
        title="Measure D",
        contest_type=ContestType.MEASURE,
        jurisdiction="Santa Clara County, CA",
        measure=measure,
    )
    lens = IssueLens(
        id="climate-environment",
        name="Climate/environment",
        description="Looks for verified statements about land, parks, climate, and conservation.",
        retrieval_terms=["open space", "parks", "wildfire"],
        limits="Does not infer a general climate position from one land-use statement.",
    )

    assert contest.measure == measure
    assert lens.id == "climate-environment"


def test_candidate_race_requires_candidates() -> None:
    with pytest.raises(ValidationError, match="candidate races require candidates"):
        Contest(
            id="bos-d1",
            election_id="ca-2026-primary",
            title="Board of Supervisors, District 1",
            contest_type=ContestType.CANDIDATE_RACE,
            jurisdiction="Santa Clara County, CA",
            candidates=[],
        )


def test_supported_finding_requires_a_cited_claim() -> None:
    with pytest.raises(ValidationError, match="supported findings require a cited summary"):
        EvidenceFinding(
            status=EvidenceStatus.SUPPORTED,
            lens_id="housing-affordability",
        )


def test_insufficient_evidence_cannot_hide_an_uncited_claim() -> None:
    with pytest.raises(ValidationError, match="unsupported findings cannot carry a factual claim"):
        EvidenceFinding(
            status=EvidenceStatus.INSUFFICIENT_EVIDENCE,
            lens_id="public-safety",
            summary=CitedClaim(
                text="This unsupported claim should be rejected.",
                citations=[
                    {
                        "source_id": "source-one",
                        "chunk_id": "chunk-one",
                        "locator": "p. 1",
                        "public_source_url": "https://example.gov/source-one.pdf",
                        "source_type": "elections_office_material",
                    }
                ],
            ),
        )


def test_brief_response_rejects_numeric_match_scores_and_recommendations() -> None:
    cited_summary = CitedClaim(
        text="Measure D is described as a parcel tax in the reviewed source.",
        citations=[
            {
                "source_id": "measure-d-analysis",
                "chunk_id": "measure-d-analysis-p1",
                "locator": "p. 1",
                "public_source_url": "https://example.gov/measure-d-analysis.pdf",
                "source_type": "elections_office_material",
            }
        ],
    )

    with pytest.raises(ValidationError):
        BriefResponse(
            election_id="ca-2026-primary",
            contest_id="measure-d",
            findings=[
                EvidenceFinding(
                    status=EvidenceStatus.SUPPORTED,
                    lens_id="climate-environment",
                    summary=cited_summary,
                )
            ],
            disclaimer="Research assistance only; not a voting recommendation.",
            match_score=82,
            recommendation="Vote yes",
        )


def test_correction_report_has_reviewable_shape() -> None:
    report = CorrectionReport(
        source_id="measure-d-analysis",
        chunk_id="measure-d-analysis-p1",
        contest_id="measure-d",
        description="The locator appears to point to the wrong page in the source snapshot.",
        submitted_at=datetime.now(UTC),
    )

    assert report.status == ReviewStatus.PENDING


def test_candidate_contract_binds_candidate_to_contest() -> None:
    candidate = Candidate(
        id="candidate-a",
        name="Example Candidate",
        contest_id="bos-d1",
    )

    assert candidate.contest_id == "bos-d1"
