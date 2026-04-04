"""Snapshots API."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_list_and_get_snapshot(api_client):  # noqa: ANN001
    r = api_client.get("/snapshots")
    assert r.status_code == 200
    rows = r.json()
    assert any(x.get("snapshot_id") == "dev_snapshot_v2" for x in rows)
    d = api_client.get("/snapshots/dev_snapshot_v2")
    assert d.status_code == 200
    body = d.json()
    assert body["snapshot_id"]
    assert "counts" in body
