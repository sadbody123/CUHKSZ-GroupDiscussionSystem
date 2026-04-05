"""Snapshot index-status endpoint."""

from __future__ import annotations


def test_index_status(api_client) -> None:
    r = api_client.get("/snapshots/dev_snapshot_v2/index-status")
    assert r.status_code == 200
    data = r.json()
    assert "has_indexes" in data
    assert "snapshot_id" in data
