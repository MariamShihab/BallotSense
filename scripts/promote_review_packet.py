"""Promote reviewer-approved excerpts into a retrieval-eligible corpus file."""

# ruff: noqa: E402, I001

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from ballotsense_api.models import SourceChunk, SourceChunkCandidate  # noqa: E402


DEFAULT_PACKET_PATH = ROOT / "data/review_packets/measure-d.json"
DEFAULT_OUTPUT_PATH = ROOT / "data/corpus/measure-d-approved-chunks.json"


def promote(packet_path: Path, output_path: Path) -> None:
    packet = json.loads(packet_path.read_text())
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    promote(args.packet, args.output)


if __name__ == "__main__":
    main()
