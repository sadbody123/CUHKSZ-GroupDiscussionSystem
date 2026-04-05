"""Group simulation API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import HAS_SNAPSHOT_V2


def test_roster_templates_list(api_client: TestClient) -> None:
    r = api_client.get("/roster-templates")
    assert r.status_code == 200
    rows = r.json()
    assert any(x.get("roster_template_id") == "gd_4p_balanced" for x in rows)


def test_create_session_with_roster(api_client: TestClient) -> None:
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
            "provider_name": "mock",
            "roster_template_id": "gd_4p_balanced",
            "user_participant_id": "for_a",
        },
    )
    assert c.status_code == 200
    sid = c.json()["session_id"]
    rr = api_client.get(f"/sessions/{sid}/roster")
    assert rr.status_code == 200
    assert rr.json().get("user_participant_id") == "for_a"
