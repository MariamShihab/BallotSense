"""Privacy-preserving ballot discovery scaffolding.

Phase 7 starts with address-based contest discovery, but only after an approved
geographic provider is selected. Until then, the resolver returns a safe manual
fallback and does not infer contests from raw address text.
"""

from .models import (
    AddressResolutionRequest,
    AddressResolutionResponse,
    BallotDiscoveryStatus,
    ContestSuggestion,
    ContestType,
)

DEMO_CONTESTS = [
    ContestSuggestion(
        contest_id="scvosa-measure-d",
        title="Measure D",
        contest_type=ContestType.MEASURE,
        jurisdiction="Santa Clara Valley Open Space Authority",
        reason="Archive-demo contest already available in the reviewed corpus.",
        confidence="manual_fallback",
    ),
    ContestSuggestion(
        contest_id="scc-bos-district-1",
        title="Board of Supervisors, District 1",
        contest_type=ContestType.CANDIDATE_RACE,
        jurisdiction="Santa Clara County, CA",
        reason=(
            "Archive-demo contest shell is available; reviewed candidate corpus "
            "is not added yet."
        ),
        confidence="manual_fallback",
    ),
]


class AddressResolver:
    """Resolve a raw address into candidate contests for this request only."""

    provider_name = "unconfigured"

    def resolve(self, request: AddressResolutionRequest) -> AddressResolutionResponse:
        raise NotImplementedError


class ProviderNotConfiguredAddressResolver(AddressResolver):
    """Safe default until the project owner approves a geographic source."""

    provider_name = "provider-not-configured"

    def resolve(self, request: AddressResolutionRequest) -> AddressResolutionResponse:
        # Deliberately do not inspect, normalize, log, or persist request.address.
        return AddressResolutionResponse(
            election_id=request.election_id,
            status=BallotDiscoveryStatus.PROVIDER_NOT_CONFIGURED,
            provider_name=self.provider_name,
            message=(
                "Address discovery is not enabled until an approved geographic "
                "provider is configured. Use manual contest selection for now."
            ),
            inferred_contests=[],
            manual_contests=DEMO_CONTESTS,
            requires_confirmation=True,
            address_retained=False,
        )
