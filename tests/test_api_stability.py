"""API stability routes."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_system_e2e_scenarios(api_client: TestClient) -> None:
    r = api_client.get("/system/e2e-scenarios")
    assert r.status_code == 200
    data = r.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 1


def test_system_stability_report(api_client: TestClient) -> None:
    r = api_client.get("/system/stability")
    assert r.status_code == 200
    assert "report" in r.json()


def test_system_release_candidate(api_client: TestClient) -> None:
    r = api_client.get("/system/release-candidate")
    assert r.status_code == 200
    assert r.json()["report"].get("go_no_go")
