"""Feedback API."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_feedback_endpoint(api_client):  # noqa: ANN001
    t = api_client.get("/topics", params={"snapshot_id": "dev_snapshot_v2"})
    tid = t.json()[0]["topic_id"]
    c = api_client.post(
        "/sessions",
        json={"snapshot_id": "dev_snapshot_v2", "topic_id": tid, "provider_name": "mock"},
    )
    sid = c.json()["session_id"]
    api_client.post(f"/sessions/{sid}/turns/user", json={"text": "Test line for feedback."})
    api_client.post(f"/sessions/{sid}/run-next")
    f = api_client.post(f"/sessions/{sid}/feedback")
    assert f.status_code == 200
    body = f.json()
    assert body.get("coach_text")
