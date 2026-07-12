import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ballotsense_api.ballot_discovery import ProviderNotConfiguredAddressResolver
from ballotsense_api.main import app, get_address_resolver
from ballotsense_api.models import AddressResolutionRequest, AddressResolutionResponse


def test_unconfigured_address_resolver_does_not_infer_or_retain_address() -> None:
    resolver = ProviderNotConfiguredAddressResolver()

    response = resolver.resolve(
        AddressResolutionRequest(
            election_id="ca-scc-2026-primary",
            address="70 W Hedding St, San Jose, CA",
        )
    )

    assert response.status == "provider_not_configured"
    assert response.inferred_contests == []
    assert response.manual_contests
    assert response.requires_confirmation is True
    assert response.address_retained is False
    assert not hasattr(response, "address")


def test_address_resolution_rejects_extra_voter_profile_fields() -> None:
    with pytest.raises(ValidationError):
        AddressResolutionRequest.model_validate(
            {
                "election_id": "ca-scc-2026-primary",
                "address": "70 W Hedding St, San Jose, CA",
                "vote_choice": "yes",
                "party": "example",
                "local_note": "private note",
            }
        )


def test_address_response_cannot_claim_raw_address_retention() -> None:
    with pytest.raises(ValidationError, match="must not retain raw address"):
        AddressResolutionResponse.model_validate(
            {
                "election_id": "ca-scc-2026-primary",
                "status": "requires_confirmation",
                "provider_name": "test",
                "message": "Unsafe response.",
                "inferred_contests": [],
                "manual_contests": [],
                "requires_confirmation": True,
                "address_retained": True,
            }
        )


def test_address_endpoint_uses_ephemeral_resolver() -> None:
    resolver = ProviderNotConfiguredAddressResolver()
    app.dependency_overrides[get_address_resolver] = lambda: resolver
    try:
        response = TestClient(app).post(
            "/v1/ballots/resolve-address",
            json={
                "election_id": "ca-scc-2026-primary",
                "address": "70 W Hedding St, San Jose, CA",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "provider_not_configured"
    assert payload["inferred_contests"] == []
    assert payload["manual_contests"][0]["contest_id"] == "scvosa-measure-d"
    assert payload["address_retained"] is False
    assert "address" not in payload


def test_address_endpoint_rejects_extra_voter_data() -> None:
    response = TestClient(app).post(
        "/v1/ballots/resolve-address",
        json={
            "election_id": "ca-scc-2026-primary",
            "address": "70 W Hedding St, San Jose, CA",
            "vote_choice": "yes",
        },
    )

    assert response.status_code == 422
