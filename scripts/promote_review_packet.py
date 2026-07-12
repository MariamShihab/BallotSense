"""Promote reviewer-approved excerpts into a retrieval-eligible corpus file."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from ballotsense_api.models import SourceChunk, SourceChunkCandidate


PACKET_PATH = ROOT / "data/review_packets/measure-d.json"
OUTPUT_PATH = ROOT / "data/corpus/measure-d-approved-chunks.json"


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text())
    if packet.get("review_decision") != "approved":
        raise ValueError("review packet must be explicitly approved before promotion")

    reviewer = packet["reviewer"]
    reviewed_at = packet["reviewed_at"]
    chunks = [SourceChunkCandidate.model_validate(chunk) for chunk in packet["chunks"]]
    approved_chunks = [
        SourceChunk(
            id=chunk.id,
            source_id=chunk.source_id,
            election_id=chunk.election_id,
            contest_id=chunk.contest_id,
            text=chunk.text,
            locator=chunk.locator,
            reviewed_at=reviewed_at,
            reviewer=reviewer,
        ).model_dump(mode="json")
        for chunk in chunks
    ]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "election_id": packet["election_id"],
                "contest_id": packet["contest_id"],
                "reviewed_at": reviewed_at,
                "reviewer": reviewer,
                "chunks": approved_chunks,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
