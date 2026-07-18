"""Snapshot and hash the official California 2024 VIG master PDF.

This script creates the authenticity anchor for the archived Proposition 36
demo corpus. It downloads the complete official voter guide, stores the exact
PDF bytes locally, computes SHA-256, and writes a JSON manifest that can be
committed to git.

The PDF itself is intentionally ignored by git because it is a large source
artifact. The manifest is the auditable record that ties every later extracted
chunk back to the exact master document.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:  # pragma: no cover - certifi is present in the dev env.
    certifi = None


ROOT = Path(__file__).parents[1]

ELECTION_ID = "ca-general-2024-11-05"
CONTEST_ID = "ca-prop-36-2024"
SOURCE_ID = "ca-2024-vig-complete"
CANONICAL_URL = "https://vig.cdn.sos.ca.gov/2024/general/pdf/complete-vig.pdf"
SNAPSHOT_DIR = ROOT / "data/source_snapshots/ca-general-2024-11-05/ca-prop-36-2024"
SNAPSHOT_PATH = SNAPSHOT_DIR / "complete-vig.pdf"
MANIFEST_PATH = SNAPSHOT_DIR / "master-pdf-manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(destination.suffix + ".tmp")
    request = Request(url, headers={"User-Agent": "BallotSense source snapshotter/0.1"})
    try:
        with urlopen(request, context=ssl_context(), timeout=60) as response:
            temp_path.write_bytes(response.read())
    except URLError as exc:  # pragma: no cover - depends on network state.
        raise RuntimeError(f"failed to fetch {url}: {exc}") from exc
    temp_path.replace(destination)


def build_manifest(*, retrieved_at: datetime, content_sha256: str, size_bytes: int) -> dict:
    return {
        "election_id": ELECTION_ID,
        "contest_id": CONTEST_ID,
        "source_id": SOURCE_ID,
        "title": "California Official Voter Information Guide, November 5, 2024 General Election",
        "publisher": "California Secretary of State",
        "canonical_url": CANONICAL_URL,
        "source_type": "state_voter_guide",
        "source_tier": 1,
        "artifact_kind": "complete official voter guide PDF",
        "retrieved_at": retrieved_at.isoformat().replace("+00:00", "Z"),
        "content_sha256": content_sha256,
        "size_bytes": size_bytes,
        "local_snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "git_tracks_pdf": False,
        "planned_snapshot_uri": (
            "gs://ballotsense-mvp-source-snapshots/"
            f"{ELECTION_ID}/{CONTEST_ID}/{SOURCE_ID}/{content_sha256}.pdf"
        ),
        "page_scope": {
            "title_summary_analysis_arguments": (
                "Official VIG PDF pages 58-63; verify during review."
            ),
            "full_text": "Official VIG PDF pages 126-134; verify during review.",
        },
        "review_status": "pending",
        "reviewer": "Project owner (user)",
        "notes": [
            "This complete PDF hash is the primary authenticity anchor.",
            "Later chunks must cite this source_id and a stable page locator.",
            "No generated summaries may be stored as chunks.",
            "No embeddings may be generated until a reviewer approves extracted chunks.",
        ],
    }


def snapshot(*, force: bool = False) -> dict:
    if force or not SNAPSHOT_PATH.exists():
        download(CANONICAL_URL, SNAPSHOT_PATH)

    content_sha256 = sha256_file(SNAPSHOT_PATH)
    manifest = build_manifest(
        retrieved_at=datetime.now(UTC),
        content_sha256=content_sha256,
        size_bytes=SNAPSHOT_PATH.stat().st_size,
    )
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="re-download even if the PDF exists")
    args = parser.parse_args()
    try:
        manifest = snapshot(force=args.force)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
