from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ballotsense_api.models import CitedClaim, ReviewStatus, SourceDocument, SourceType


def test_approved_source_requires_review_timestamp() -> None:
    with pytest.raises(ValidationError, match="approved sources require reviewed_at"):
        SourceDocument(
            id="ca-primary-guide",
            title="Example guide",
            canonical_url="https://example.gov/guide.pdf",
            publisher="Example County",
            source_type=SourceType.COUNTY_VOTER_GUIDE,
            election_id="ca-2026-primary",
            jurisdiction="Example County, CA",
            retrieved_at=datetime.now(UTC),
            content_sha256="a" * 64,
            review_status=ReviewStatus.APPROVED,
        )


def test_displayable_claim_requires_citation() -> None:
    with pytest.raises(ValidationError):
        CitedClaim(text="A statement without evidence.", citations=[])
