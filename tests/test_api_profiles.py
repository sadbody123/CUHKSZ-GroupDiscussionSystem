"""Profiles API."""

from __future__ import annotations


def test_profiles_list(api_client):  # noqa: ANN001
    r = api_client.get("/profiles")
    assert r.status_code == 200
    rows = r.json()
    assert any(x.get("profile_id") == "default" for x in rows)


def test_profile_detail(api_client):  # noqa: ANN001
    r = api_client.get("/profiles/default")
    assert r.status_code == 200
    assert r.json()["profile"]["profile_id"] == "default"


def test_create_session_with_profile(api_client):  # noqa: ANN001
    from tests.conftest import HAS_SNAPSHOT_V2

    if not HAS_SNAPSHOT_V2:
        import pytest

        pytest.skip("no snapshot")
    t = api_client.get("/topics", params={"snapshot_id": "dev_snapshot_v2"})
    tid = t.json()[0]["topic_id"]
    c = api_client.post(
        "/sessions",
        json={
            "snapshot_id": "dev_snapshot_v2",
            "topic_id": tid,
            "runtime_profile_id": "concise",
            "provider_name": "mock",
        },
    )
    assert c.status_code == 200
    assert c.json().get("runtime_profile_id") == "concise"
    sid = c.json()["session_id"]
    g = api_client.get(f"/sessions/{sid}")
    assert g.json().get("runtime_profile_id") == "concise"
