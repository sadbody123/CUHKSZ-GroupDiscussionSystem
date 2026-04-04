"""API end-to-end MVP (mock provider)."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_e2e_create_turn_run_auto_feedback_export(api_client):  # noqa: ANN001
    t = api_client.get("/topics", params={"snapshot_id": "dev_snapshot_v2"})
    tid = t.json()[0]["topic_id"]
    c = api_client.post(
        "/sessions",
        json={
            "snapshot_id": "dev_snapshot_v2",
            "topic_id": tid,
            "user_stance": "for",
            "provider_name": "mock",
        },
    )
    sid = c.json()["session_id"]
    api_client.post(f"/sessions/{sid}/turns/user", json={"text": "E2E user line."})
    api_client.post(f"/sessions/{sid}/run-next")
    api_client.post(f"/sessions/{sid}/auto-run", json={"max_steps": 2})
    api_client.post(f"/sessions/{sid}/feedback")
    ex = api_client.get(f"/sessions/{sid}/export")
    assert ex.status_code == 200
    assert ex.json()["session_id"] == sid
