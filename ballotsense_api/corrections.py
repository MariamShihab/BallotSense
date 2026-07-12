"""Privacy-preserving correction report workflow."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from uuid import uuid4

from google.cloud import firestore

from .models import (
    CorrectionReportRecord,
    CorrectionReportRequest,
    CorrectionReportResponse,
    ReviewStatus,
)

EMAIL_PATTERN = re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
STREET_PATTERN = re.compile(
    r"\b\d{1,6}\s+[\w .'-]{2,60}\s+"
    r"(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct|way|boulevard|blvd)\b",
    re.IGNORECASE,
)
VOTE_PREFERENCE_PATTERN = re.compile(
    r"\b(?:i|we)\s+(?:already\s+)?(?:will|would|plan to|intend to|am going to|"
    r"are going to|voted|vote)\s+(?:vote\s+)?(?:yes|no|for|against)\b",
    re.IGNORECASE,
)


class CorrectionReportRepository:
    def record(self, report: CorrectionReportRecord) -> None:
        raise NotImplementedError


class InMemoryCorrectionReportRepository(CorrectionReportRepository):
    def __init__(self) -> None:
        self.records: list[CorrectionReportRecord] = []

    def record(self, report: CorrectionReportRecord) -> None:
        self.records.append(report)


class FirestoreCorrectionReportRepository(CorrectionReportRepository):
    def __init__(self, client: firestore.Client) -> None:
        self._client = client

    def record(self, report: CorrectionReportRecord) -> None:
        self._client.collection("correction_reports").document(report.id).set(
            report.model_dump(mode="json")
        )


class CorrectionService:
    def __init__(self, repository: CorrectionReportRepository) -> None:
        self._repository = repository

    def submit(self, request: CorrectionReportRequest) -> CorrectionReportResponse:
        redacted_description, redaction_applied = redact_report_text(request.description)
        report = CorrectionReportRecord(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            election_id=request.election_id,
            contest_id=request.contest_id,
            lens_id=request.lens_id,
            source_id=request.source_id,
            chunk_id=request.chunk_id,
            issue_type=request.issue_type,
            redacted_description=redacted_description,
            redaction_applied=redaction_applied,
            status=ReviewStatus.PENDING,
        )
        self._repository.record(report)
        return CorrectionReportResponse(
            report_id=report.id,
            status=report.status,
            message="Correction report received for reviewer follow-up.",
        )


def redact_report_text(text: str) -> tuple[str, bool]:
    redacted = text
    redacted = EMAIL_PATTERN.sub("[redacted-email]", redacted)
    redacted = PHONE_PATTERN.sub("[redacted-phone]", redacted)
    redacted = STREET_PATTERN.sub("[redacted-address]", redacted)
    redacted = VOTE_PREFERENCE_PATTERN.sub("[redacted-vote-preference]", redacted)
    return redacted, redacted != text


def build_firestore_correction_service(project_id: str) -> CorrectionService:
    client = firestore.Client(project=project_id)
    return CorrectionService(FirestoreCorrectionReportRepository(client))
