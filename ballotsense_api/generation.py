"""Bounded Gemini generation and deterministic citation validation.

No text is eligible for display until ``CitedBriefValidator`` has verified it
against the exact evidence packet supplied to Gemini for that request.
"""

from __future__ import annotations

import os
import re

from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from .models import (
    BriefRequest,
    BriefResponse,
    Citation,
    EvidenceFinding,
    EvidenceStatus,
    RetrievedChunk,
    SourceType,
)

DEFAULT_DISCLAIMER = "Research assistance only; BallotSense does not recommend or rank choices."
PROHIBITED_LANGUAGE = re.compile(
    r"\b(vote\s+(?:yes|no|for)|should\s+vote|recommend(?:ed|ation)?|best\s+choice|"
    r"better\s+choice|match\s+score|rank(?:ing|ed)?)\b",
    re.IGNORECASE,
)


class EvidencePacketChunk(BaseModel):
    """One reviewed excerpt, with all metadata Gemini may use to cite it."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    chunk_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    election_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    contest_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{2,127}$")
    source_type: SourceType
    source_tier: int = Field(ge=1, le=3)
    locator: str = Field(min_length=1, max_length=240)
    public_source_url: HttpUrl
    text: str = Field(min_length=1, max_length=10_000)

    @classmethod
    def from_retrieved_chunk(
        cls, chunk: RetrievedChunk, public_source_url: str
    ) -> EvidencePacketChunk:
        return cls(
            source_id=chunk.source_id,
            chunk_id=chunk.chunk_id,
            election_id=chunk.election_id,
            contest_id=chunk.contest_id,
            source_type=chunk.source_type,
            source_tier=chunk.source_tier,
            locator=chunk.locator,
            public_source_url=public_source_url,
            text=chunk.text,
        )


class EvidencePacket(BaseModel):
    """The complete and exclusive evidence boundary for one generated brief."""

    model_config = ConfigDict(extra="forbid")

    request: BriefRequest
    chunks: list[EvidencePacketChunk] = Field(min_length=1, max_length=12)


class InvalidBriefOutput(ValueError):
    """Raised when model output cannot safely become a voter-facing response."""


class CitedBriefValidator:
    """Validate citations, scope, attribution, and non-recommendation rules."""

    def validate(self, response: BriefResponse, evidence: EvidencePacket) -> BriefResponse:
        if response.election_id != evidence.request.election_id:
            raise InvalidBriefOutput("response election does not match the evidence request")
        if response.contest_id != evidence.request.contest_id:
            raise InvalidBriefOutput("response contest does not match the evidence request")
        if set(finding.lens_id for finding in response.findings) - set(evidence.request.lens_ids):
            raise InvalidBriefOutput("response contains an unrequested issue lens")

        evidence_by_id = {(chunk.source_id, chunk.chunk_id): chunk for chunk in evidence.chunks}
        for finding in response.findings:
            self._validate_finding(finding, evidence_by_id)
        return response

    def _validate_finding(
        self,
        finding: EvidenceFinding,
        evidence_by_id: dict[tuple[str, str], EvidencePacketChunk],
    ) -> None:
        if finding.status != EvidenceStatus.SUPPORTED:
            return
        assert finding.summary is not None  # guaranteed by the response contract
        if PROHIBITED_LANGUAGE.search(finding.summary.text):
            raise InvalidBriefOutput("claim contains prohibited recommendation or ranking language")
        for citation in finding.summary.citations:
            self._validate_citation(citation, evidence_by_id)

    @staticmethod
    def _validate_citation(
        citation: Citation,
        evidence_by_id: dict[tuple[str, str], EvidencePacketChunk],
    ) -> None:
        evidence_chunk = evidence_by_id.get((citation.source_id, citation.chunk_id))
        if evidence_chunk is None:
            raise InvalidBriefOutput("citation does not reference supplied evidence")
        if (
            citation.locator != evidence_chunk.locator
            or citation.source_type != evidence_chunk.source_type
            or str(citation.public_source_url) != str(evidence_chunk.public_source_url)
        ):
            raise InvalidBriefOutput("citation metadata does not match supplied evidence")


class GeminiCitedBriefGenerator:
    """Ask Gemini for JSON constrained to the evidence packet, never user data."""

    def __init__(self, project_id: str, model: str = "gemini-2.5-flash") -> None:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
        self._client = genai.Client()
        self._model = model

    def generate(
        self, evidence: EvidencePacket, corrective_feedback: str | None = None
    ) -> BriefResponse:
        response = self._client.models.generate_content(
            model=self._model,
            contents=self._prompt(evidence, corrective_feedback),
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=1_200,
                response_mime_type="application/json",
                response_schema=BriefResponse,
            ),
        )
        if not response.text:
            raise InvalidBriefOutput("Gemini returned no structured response")
        parsed = BriefResponse.model_validate_json(response.text)
        return CitedBriefValidator().validate(parsed, evidence)

    @staticmethod
    def _prompt(evidence: EvidencePacket, corrective_feedback: str | None = None) -> str:
        prompt = (
            "You are BallotSense's citation-first research assistant. Use ONLY the evidence "
            "packet below; do not use background knowledge, inference, or any omitted source. "
            "Return JSON matching the provided schema. For every factual statement, provide one "
            "or more citations copied exactly from the packet. Preserve attribution for ballot "
            "arguments and campaign materials. Do not endorse, recommend, rank, score, or tell a "
            "person how to vote. If the packet lacks support for a requested lens, return an "
            "insufficient_evidence finding with an explanation and no summary.\n\n"
            f"Evidence packet:\n{evidence.model_dump_json(indent=2)}"
        )
        if corrective_feedback is not None:
            prompt += f"\n\nCorrective feedback from the validator: {corrective_feedback}"
        return prompt


def safe_insufficient_evidence_response(request: BriefRequest) -> BriefResponse:
    """A safe fallback when model output fails validation or evidence is unavailable."""

    return BriefResponse(
        election_id=request.election_id,
        contest_id=request.contest_id,
        findings=[
            EvidenceFinding(
                status=EvidenceStatus.INSUFFICIENT_EVIDENCE,
                lens_id=lens_id,
                explanation="BallotSense could not verify enough reviewed evidence for this lens.",
            )
            for lens_id in request.lens_ids
        ],
        disclaimer=DEFAULT_DISCLAIMER,
    )


def safe_not_covered_response(request: BriefRequest) -> BriefResponse:
    """A safe fallback when no reviewed corpus exists for the requested contest."""

    return BriefResponse(
        election_id=request.election_id,
        contest_id=request.contest_id,
        findings=[
            EvidenceFinding(
                status=EvidenceStatus.NOT_COVERED,
                lens_id=lens_id,
                explanation=(
                    "BallotSense does not yet have a reviewed source corpus for this contest."
                ),
            )
            for lens_id in request.lens_ids
        ],
        disclaimer=DEFAULT_DISCLAIMER,
    )
