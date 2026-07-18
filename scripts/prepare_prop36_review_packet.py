"""Prepare a pending reviewer packet from the Prop 36 master PDF snapshot.

The output is intentionally *not* a retrieval corpus. It is a review packet of
verbatim page-level extraction candidates. A human reviewer must compare the
text to the official PDF pages, trim/reject where needed, and set
``review_decision`` to ``approved`` before promotion and embedding can happen.
"""

# ruff: noqa: E402, I001

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from ballotsense_api.models import ExtractionStatus, SourceChunkCandidate  # noqa: E402
from scripts.snapshot_prop36_master_pdf import (  # noqa: E402
    CONTEST_ID,
    ELECTION_ID,
    MANIFEST_PATH,
    SNAPSHOT_PATH,
    SOURCE_ID,
    sha256_file,
)


OUTPUT_PATH = ROOT / "data/review_packets/prop-36-2024.json"
SOURCE_RECORD_PATH = ROOT / "data/source_records/prop-36-2024.json"
SOURCE_CANDIDATE_PATH = ROOT / "data/source_candidates/prop-36-2024.json"
PAGE_RANGES = {
    "title-summary-analysis-arguments": range(58, 64),
    "full-text": range(126, 135),
}


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            "missing master PDF manifest; run scripts/snapshot_prop36_master_pdf.py first"
        )
    manifest = json.loads(MANIFEST_PATH.read_text())
    if not SNAPSHOT_PATH.exists():
        raise FileNotFoundError(
            f"missing local PDF snapshot at {SNAPSHOT_PATH}; "
            "run scripts/snapshot_prop36_master_pdf.py first"
        )
    observed_hash = sha256_file(SNAPSHOT_PATH)
    if observed_hash != manifest["content_sha256"]:
        raise ValueError(
            "local PDF hash mismatch; refusing extraction from a non-manifest artifact"
        )
    return manifest


def require_pypdf():
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "pypdf is required for Prop 36 text extraction. "
            "Install project dependencies, then rerun this script."
        ) from exc
    return PdfReader


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_texts() -> dict[int, str]:
    PdfReader = require_pypdf()
    reader = PdfReader(str(SNAPSHOT_PATH))
    extracted: dict[int, str] = {}
    for page_number in sorted({page for pages in PAGE_RANGES.values() for page in pages}):
        index = page_number - 1
        if index >= len(reader.pages):
            raise ValueError(f"PDF has no page {page_number}")
        text = clean_text(reader.pages[index].extract_text() or "")
        if not text:
            raise ValueError(f"page {page_number} produced no extractable text")
        extracted[page_number] = text
    return extracted


def slice_from(text: str, start: str, *, end: str | None = None) -> str:
    if start not in text:
        raise ValueError(f"could not locate start marker: {start}")
    sliced = text[text.index(start) :]
    if end is not None:
        if end not in sliced:
            raise ValueError(f"could not locate end marker: {end}")
        sliced = sliced[: sliced.index(end)]
    return clean_text(sliced)


def make_candidate(
    *,
    chunk_id: str,
    text: str,
    locator: str,
    reviewer_note: str,
    status: ExtractionStatus = ExtractionStatus.NEEDS_REVIEWER_COMPARISON,
) -> dict:
    candidate = SourceChunkCandidate(
        id=chunk_id,
        source_id=SOURCE_ID,
        election_id=ELECTION_ID,
        contest_id=CONTEST_ID,
        text=text,
        locator=locator,
        extraction_method="digital PDF text extraction from master snapshot",
        extraction_status=status,
        reviewer_note=reviewer_note,
    )
    return candidate.model_dump(mode="json")


def build_candidate_chunks(extracted_pages: dict[int, str]) -> list[dict]:
    page_58 = extracted_pages[58]
    page_59 = extracted_pages[59]
    page_60 = extracted_pages[60]
    page_61 = extracted_pages[61]
    page_62 = extracted_pages[62]
    page_63 = extracted_pages[63]

    chunks: list[dict] = [
        make_candidate(
            chunk_id="ca-prop-36-2024-title-summary",
            text=slice_from(page_58, "PROPOSITION ALLOWS", end="ANALYSIS BY"),
            locator="Official VIG PDF p. 58, title and summary",
            status=ExtractionStatus.READY_FOR_REVIEW,
            reviewer_note=(
                "Neutral Attorney General title/summary candidate. Compare bullets and fiscal "
                "summary against p. 58 before approval."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-lao-background",
            text=clean_text(
                slice_from(page_58, "ANALYSIS BY")
                + "\n\n"
                + slice_from(page_59, "misdemeanors.", end="PROPOSAL")
            ),
            locator="Official VIG PDF pp. 58-59, LAO background",
            reviewer_note=(
                "Neutral Legislative Analyst background. Confirm the cross-page join and "
                "consider trimming repeated headers before approval."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-lao-proposal",
            text=clean_text(
                slice_from(page_59, "PROPOSAL")
                + "\n\n"
                + slice_from(page_60, "get treatment", end="FISCAL EFFECTS")
            ),
            locator="Official VIG PDF pp. 59-60, LAO proposal description",
            reviewer_note=(
                "Neutral Legislative Analyst proposal description. Confirm theft, drug, "
                "treatment-mandated felony, and warning sections before approval."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-lao-fiscal-effects",
            text=clean_text(
                slice_from(page_60, "FISCAL EFFECTS")
                + "\n\n"
                + slice_from(page_61, "community supervision.", end="Visit sos.ca.gov")
            ),
            locator="Official VIG PDF pp. 60-61, LAO fiscal effects",
            reviewer_note=(
                "Neutral Legislative Analyst fiscal-effects candidate. Confirm state/local "
                "cost estimates and Proposition 47 savings language before approval."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-argument-in-favor",
            text=slice_from(
                page_62,
                "★  ARGUMENT IN FAVOR OF PROPOSITION 36",
                end="★  REBUTTAL TO ARGUMENT IN FAVOR OF PROPOSITION 36",
            ),
            locator="Official VIG PDF p. 62, argument in favor",
            reviewer_note=(
                "Attributed ballot argument. Do not treat as neutral fact; preserve authorship "
                "and VIG accuracy disclaimer in UI/source labels."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-rebuttal-to-favor",
            text=slice_from(
                page_62,
                "★  REBUTTAL TO ARGUMENT IN FAVOR OF PROPOSITION 36",
                end="62 | Arguments",
            ),
            locator="Official VIG PDF p. 62, rebuttal to argument in favor",
            reviewer_note=(
                "Attributed rebuttal by opponents. Do not treat as neutral fact; compare full "
                "wording and author list before approval."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-argument-against",
            text=slice_from(
                page_63,
                "★  ARGUMENT AGAINST PROPOSITION 36",
                end="★  REBUTTAL TO ARGUMENT AGAINST PROPOSITION 36",
            ),
            locator="Official VIG PDF p. 63, argument against",
            reviewer_note=(
                "Attributed ballot argument. Do not treat as neutral fact; compare full "
                "wording and author list before approval."
            ),
        ),
        make_candidate(
            chunk_id="ca-prop-36-2024-rebuttal-to-against",
            text=slice_from(
                page_63,
                "★  REBUTTAL TO ARGUMENT AGAINST PROPOSITION 36",
                end="Arguments printed on this page",
            ),
            locator="Official VIG PDF p. 63, rebuttal to argument against",
            reviewer_note=(
                "Attributed rebuttal by proponents. Do not treat as neutral fact; compare full "
                "wording and author list before approval."
            ),
        ),
    ]

    for page_number in PAGE_RANGES["full-text"]:
        text = extracted_pages[page_number]
        if page_number == 126:
            text = slice_from(text, "PROPOSITION 36")
        chunks.append(
            make_candidate(
                chunk_id=f"ca-prop-36-2024-text-p{page_number:03d}",
                text=text,
                locator=f"Official VIG PDF p. {page_number}, text of proposed laws",
                reviewer_note=(
                    "Official measure-text page candidate. Reviewer should compare against the "
                    "PDF page and decide whether to keep page-level chunks or split by statute "
                    "section before approval."
                ),
            )
        )
    return chunks


def write_source_candidate(manifest: dict) -> None:
    candidate = {
        "election_id": ELECTION_ID,
        "contest_id": CONTEST_ID,
        "jurisdiction": "California",
        "reviewer": "Project owner (user)",
        "sources": [
            {
                "id": SOURCE_ID,
                "title": manifest["title"],
                "canonical_url": manifest["canonical_url"],
                "publisher": manifest["publisher"],
                "expected_source_type": "state_voter_guide",
                "source_tier": 1,
                "election_id": ELECTION_ID,
                "jurisdiction": "California",
                "contest_id": CONTEST_ID,
                "document_role": (
                    "official Prop 36 title, summary, Legislative Analyst analysis, "
                    "arguments, rebuttals, and measure text"
                ),
                "artifact_kind": "PDF",
                "has_stable_locator": True,
                "inclusion_reason": (
                    "The California Secretary of State official voter guide is the primary "
                    "neutral government source for statewide Proposition 36."
                ),
                "attribution_note": (
                    "Tier 1 state voter guide. Ballot arguments inside the guide must still "
                    "be attributed to their named proponents/opponents."
                ),
                "retrieved_at": manifest["retrieved_at"],
                "published_at": None,
                "status": "pending_review",
                "reviewer": "Project owner (user)",
                "review_note": "Pending reviewer comparison against the master PDF snapshot.",
            }
        ],
        "known_gap": (
            "This packet uses the complete official guide as one master source. "
            "Chunk-level review must separate neutral analysis from attributed arguments."
        ),
    }
    SOURCE_CANDIDATE_PATH.write_text(json.dumps(candidate, indent=2) + "\n")


def write_source_record(manifest: dict) -> None:
    record = {
        "election_id": ELECTION_ID,
        "contest_id": CONTEST_ID,
        "retrieval_batch_at": manifest["retrieved_at"],
        "sources": [
            {
                "id": SOURCE_ID,
                "title": manifest["title"],
                "canonical_url": manifest["canonical_url"],
                "publisher": manifest["publisher"],
                "source_type": "state_voter_guide",
                "source_tier": 1,
                "election_id": ELECTION_ID,
                "jurisdiction": "California",
                "contest_id": CONTEST_ID,
                "retrieved_at": manifest["retrieved_at"],
                "published_at": None,
                "content_sha256": manifest["content_sha256"],
                "snapshot_uri": manifest["planned_snapshot_uri"],
                "corpus_release_id": None,
                "review_status": "pending",
                "reviewed_at": None,
                "reviewer": "Project owner (user)",
            }
        ],
    }
    SOURCE_RECORD_PATH.write_text(json.dumps(record, indent=2) + "\n")


def write_review_packet(manifest: dict, chunks: list[dict]) -> None:
    packet = {
        "election_id": ELECTION_ID,
        "contest_id": CONTEST_ID,
        "source_id": SOURCE_ID,
        "corpus_target": "archived-california-november-2024-proposition-36-demo-corpus",
        "reviewer": "Project owner (user)",
        "reviewed_at": None,
        "review_decision": "pending",
        "master_pdf_sha256": manifest["content_sha256"],
        "master_pdf_canonical_url": manifest["canonical_url"],
        "chunking_policy": [
            "Chunks are verbatim page-level extraction candidates, not summaries.",
            "Reviewer must trim/reject text that is not part of Proposition 36.",
            "Reviewer must preserve whether text is neutral analysis or an attributed argument.",
            "Only approved chunks may be promoted to data/corpus and embedded.",
        ],
        "chunks": chunks,
    }
    OUTPUT_PATH.write_text(json.dumps(packet, indent=2) + "\n")


def prepare() -> dict:
    manifest = load_manifest()
    extracted_pages = page_texts()
    chunks = build_candidate_chunks(extracted_pages)
    SOURCE_CANDIDATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_source_candidate(manifest)
    write_source_record(manifest)
    write_review_packet(manifest, chunks)
    coverage = {
        "election_id": ELECTION_ID,
        "contest_id": CONTEST_ID,
        "updated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "current_target": "Archived California November 2024 Proposition 36 demo corpus",
        "master_pdf_manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "review_packet": str(OUTPUT_PATH.relative_to(ROOT)),
        "reviewer_checklist": "docs/prop36-reviewer-checklist.md",
        "source_record": str(SOURCE_RECORD_PATH.relative_to(ROOT)),
        "chunk_candidate_count": len(chunks),
        "status": "pending_reviewer_approval",
        "acceptance_gate": [
            "Master PDF snapshot exists and matches SHA-256 manifest.",
            "Source record remains pending until reviewer approval.",
            "Chunks are extraction candidates only; they are not retrievable.",
            "No embeddings are generated before approved corpus promotion.",
        ],
        "deliberate_gap": (
            "Until review is complete, every voter-facing Prop 36 query must abstain or "
            "show pending-review status."
        ),
    }
    coverage_path = ROOT / "data/coverage/prop-36-2024-phase-2.json"
    coverage_path.write_text(json.dumps(coverage, indent=2) + "\n")
    return {
        "chunks": len(chunks),
        "review_packet": str(OUTPUT_PATH.relative_to(ROOT)),
        "coverage_matrix": str(coverage_path.relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    try:
        result = prepare()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
