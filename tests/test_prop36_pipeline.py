from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.promote_review_packet import promote
from scripts.snapshot_prop36_master_pdf import build_manifest, sha256_file


def test_sha256_file_hashes_exact_bytes(tmp_path: Path) -> None:
    artifact = tmp_path / "source.pdf"
    artifact.write_bytes(b"official bytes")

    assert sha256_file(artifact) == (
        "62dbe6d8f9a2196315f659ab2e1776b2f1283428daba85f89cdd22a950c6dc5a"
    )


def test_prop36_manifest_marks_pdf_as_uncommitted() -> None:
    manifest = build_manifest(
        retrieved_at=__import__("datetime").datetime(
            2026, 7, 18, tzinfo=__import__("datetime").UTC
        ),
        content_sha256="a" * 64,
        size_bytes=123,
    )

    assert manifest["contest_id"] == "ca-prop-36-2024"
    assert manifest["git_tracks_pdf"] is False
    assert manifest["review_status"] == "pending"
    assert manifest["planned_snapshot_uri"].endswith(f"/{'a' * 64}.pdf")


def test_promote_refuses_pending_prop36_review_packet(tmp_path: Path) -> None:
    packet = tmp_path / "packet.json"
    output = tmp_path / "approved.json"
    packet.write_text(
        json.dumps(
            {
                "election_id": "ca-general-2024-11-05",
                "contest_id": "ca-prop-36-2024",
                "review_decision": "pending",
                "reviewer": "Project owner (user)",
                "reviewed_at": None,
                "chunks": [],
            }
        )
    )

    with pytest.raises(ValueError, match="must be explicitly approved"):
        promote(packet, output)

    assert not output.exists()
