"""API health and system routes."""

from __future__ import annotations


def test_health_fields(api_client) -> None:
    r = api_client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "default_provider" in data
    assert "app_env" in data
    assert "default_runtime_profile" in data
    assert r.headers.get("X-Request-ID")


def test_system_info(api_client) -> None:
    r = api_client.get("/system/info")
    assert r.status_code == 200
    data = r.json()
    assert data["app_name"]
    assert "snapshot_root" in data
    assert "bundle_dir" in data
    assert r.headers.get("X-Request-ID")
