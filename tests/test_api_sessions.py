"""Sessions API."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_session_flow_mock(api_client):  # noqa: ANN001
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
    assert c.status_code == 200
    sid = c.json()["session_id"]
    g = api_client.get(f"/sessions/{sid}")
    assert g.status_code == 200
    u = api_client.post(f"/sessions/{sid}/turns/user", json={"text": "Opening line for API test."})
    assert u.status_code == 200
    n = api_client.post(f"/sessions/{sid}/run-next")
    assert n.status_code == 200
    a = api_client.post(f"/sessions/{sid}/auto-run", json={"max_steps": 2})
    assert a.status_code == 200
