"""API contract for Streamlit UI: same sequence the manual UI demo relies on (mock provider).

See ``docs/DEMO_UI_CHECKLIST.md`` for the human-readable walkthrough.
"""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built; run: python main.py bootstrap-dev-snapshot")
def test_ui_critical_api_chain(api_client):  # noqa: ANN001
    h = api_client.get("/health")
    assert h.status_code == 200
    assert h.json().get("status") == "ok"

    snaps = api_client.get("/snapshots")
    assert snaps.status_code == 200
    assert any(s.get("snapshot_id") == "dev_snapshot_v2" for s in snaps.json())

    t = api_client.get("/topics", params={"snapshot_id": "dev_snapshot_v2"})
    assert t.status_code == 200
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

    u = api_client.post(f"/sessions/{sid}/turns/user", json={"text": "UI checklist user line."})
    assert u.status_code == 200

    n = api_client.post(f"/sessions/{sid}/run-next")
    assert n.status_code == 200

    f = api_client.post(f"/sessions/{sid}/feedback")
    assert f.status_code == 200
    body = f.json()
    assert body.get("coach_text")
