import json
from pathlib import Path

from ballotsense_api.models import EvidenceStatus


def test_phase_four_evaluation_set_has_fixed_coverage_and_negative_cases() -> None:
    path = Path(__file__).parents[1] / "data/evaluations/measure-d-v1.json"
    evaluation_set = json.loads(path.read_text())

    assert evaluation_set["corpus_release_id"] == "measure-d-review-2026-07-12"
    statuses = {case["expected_status"] for case in evaluation_set["cases"]}
    assert EvidenceStatus.SUPPORTED in statuses
    assert EvidenceStatus.INSUFFICIENT_EVIDENCE in statuses
    assert evaluation_set["out_of_scope_cases"][0]["expected_status"] == EvidenceStatus.NOT_COVERED
    assert {
        "fabricated_citation",
        "wrong_contest_citation",
        "uncited_factual_statement",
        "recommendation_or_ranking_language",
        "party_based_inference",
    } <= set(evaluation_set["automated_negative_cases"])
