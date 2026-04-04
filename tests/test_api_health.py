"""Health endpoint."""

from __future__ import annotations


def test_health(api_client):  # noqa: ANN001
    r = api_client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["default_provider"] == "mock"
