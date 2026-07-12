from fastapi.testclient import TestClient

from ballotsense_api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_catalog_is_safe_until_sources_are_reviewed() -> None:
    response = client.get("/v1/sources?election_id=ca-2026-primary")
    assert response.status_code == 200
    assert response.json() == {"sources": []}
