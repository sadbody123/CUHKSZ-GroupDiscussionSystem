"""Snapshot loader tests."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2

from app.runtime.snapshot_loader import load_snapshot


@pytest.mark.skipif(
    not HAS_SNAPSHOT_V2,
    reason="dev_snapshot_v2 not present; run phase-2 build-offline first",
)
def test_load_full_snapshot(snapshot_v2_dir):
    b = load_snapshot(snapshot_v2_dir)
    assert b.manifest.snapshot_id
    assert len(b.normalized_docs) > 0
    assert len(b.evidence_chunks) > 0
    assert len(b.pedagogy_items) >= 0
    assert len(b.topic_cards) > 0
    assert len(b.evidence_index) > 0
