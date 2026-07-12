"""Generate one development-only cited brief from reviewed Firestore evidence.

This command accepts no voter data. It is intentionally limited to an election,
contest, and selected issue lenses, then validates Gemini output before printing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from google.cloud import firestore  # noqa: E402

from ballotsense_api.generation import (  # noqa: E402
    EvidencePacket,
    EvidencePacketChunk,
    GeminiCitedBriefGenerator,
    safe_insufficient_evidence_response,
)
from ballotsense_api.models import BriefRequest, RetrievalRequest, SourceDocument  # noqa: E402
from ballotsense_api.retrieval import FirestoreRetriever, VertexQueryEmbedder  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--election-id", required=True)
    parser.add_argument("--contest-id", required=True)
    parser.add_argument("--lens", action="append", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--source-records",
        type=Path,
        default=Path("data/source_records/measure-d.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = BriefRequest(
        election_id=args.election_id,
        contest_id=args.contest_id,
        lens_ids=args.lens,
    )
    # RetrievalRequest and BriefRequest deliberately differ: a query is required
    # for retrieval, while a brief can represent several selected lenses.
    # Construct it separately so no voter attributes are introduced.
    retrieval = FirestoreRetriever(
        firestore.Client(project=args.project), VertexQueryEmbedder(args.project)
    ).retrieve(
        RetrievalRequest(
            election_id=request.election_id,
            contest_id=request.contest_id,
            lens_id=request.lens_ids[0],
            query_text=args.query,
        )
    )
    if not retrieval.chunks:
        print(safe_insufficient_evidence_response(request).model_dump_json(indent=2))
        return

    records = json.loads(args.source_records.read_text())
    sources = {
        source.id: source
        for source in (SourceDocument.model_validate(item) for item in records["sources"])
    }
    packet = EvidencePacket(
        request=request,
        chunks=[
            EvidencePacketChunk.from_retrieved_chunk(
                chunk, str(sources[chunk.source_id].canonical_url)
            )
            for chunk in retrieval.chunks
        ],
    )
    print(GeminiCitedBriefGenerator(args.project).generate(packet).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
