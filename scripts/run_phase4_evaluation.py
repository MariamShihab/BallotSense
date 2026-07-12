"""Run the fixed Phase 4 acceptance set against the locally configured API.

This development command sends only election, contest, and lens IDs. Each API
call creates a redacted claim audit in the configured development project.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from ballotsense_api.main import app  # noqa: E402


def main() -> None:
    if "BALLOTSENSE_GCP_PROJECT" not in os.environ:
        raise SystemExit("BALLOTSENSE_GCP_PROJECT must be set")

    evaluation_path = ROOT / "data/evaluations/measure-d-v1.json"
    evaluation_set = json.loads(evaluation_path.read_text())
    client = TestClient(app)
    all_cases = [
        *evaluation_set["cases"],
        *[
            {
                **case,
                "election_id": evaluation_set["election_id"],
            }
            for case in evaluation_set["out_of_scope_cases"]
        ],
    ]
    results = []
    for case in all_cases:
        response = client.post(
            "/v1/briefs",
            json={
                "election_id": case.get("election_id", evaluation_set["election_id"]),
                "contest_id": case.get("contest_id", evaluation_set["contest_id"]),
                "lens_ids": [case["lens_id"]],
            },
        )
        body = response.json()
        actual_status = body["findings"][0]["status"] if response.status_code == 200 else "error"
        results.append(
            {
                "id": case["id"],
                "expected_status": case["expected_status"],
                "actual_status": actual_status,
                "passed": actual_status == case["expected_status"],
                "response": body,
            }
        )
    print(json.dumps({"corpus_release_id": evaluation_set["corpus_release_id"], "results": results}, indent=2))


if __name__ == "__main__":
    main()
