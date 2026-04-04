"""Topics API."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_topics_list_and_detail(api_client):  # noqa: ANN001
    r = api_client.get("/topics", params={"snapshot_id": "dev_snapshot_v2"})
    assert r.status_code == 200
    topics = r.json()
    assert topics
    tid = topics[0]["topic_id"]
    d = api_client.get(f"/topics/{tid}", params={"snapshot_id": "dev_snapshot_v2"})
    assert d.status_code == 200
    assert d.json()["card"]["topic_id"] == tid
