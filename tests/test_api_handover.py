"""Handover / final delivery API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_system_final_release_summary(api_client: TestClient) -> None:
    r = api_client.get("/system/final-release-summary")
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body
    s = body["summary"]
    assert s.get("profile_id")


def test_system_release_manifest(api_client: TestClient) -> None:
    r = api_client.get("/system/release-manifest", params={"profile_id": "v1_demo"})
    assert r.status_code == 200
    assert "manifest" in r.json()


def test_system_bom(api_client: TestClient) -> None:
    r = api_client.get("/system/bom", params={"profile_id": "v1_demo"})
    assert r.status_code == 200
    data = r.json()
    assert "bom" in data or "entry_count" in data


def test_system_verify_delivery(api_client: TestClient) -> None:
    r = api_client.post("/system/verify-delivery", params={"profile_id": "v1_demo"})
    assert r.status_code == 200
    rep = r.json().get("report") or {}
    assert rep.get("overall_status") in ("ok", "warning", "blocked")


def test_system_acceptance(api_client: TestClient) -> None:
    r = api_client.get("/system/acceptance", params={"profile_id": "v1_demo"})
    assert r.status_code == 200
    ev = r.json().get("evidence") or {}
    assert ev.get("profile_id") == "v1_demo"
