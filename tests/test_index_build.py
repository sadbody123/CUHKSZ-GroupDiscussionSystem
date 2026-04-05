"""Offline index build."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.offline_build.indexes.builder import build_snapshot_indexes
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no dev_snapshot_v2")
def test_build_indexes_smoke(tmp_path: Path) -> None:
    dst = tmp_path / "snap"
    shutil.copytree(SNAPSHOT_V2, dst / "dev_snapshot_v2")
    snap = dst / "dev_snapshot_v2"
    man = build_snapshot_indexes(
        snap,
        stores=["evidence", "pedagogy", "topics"],
        modes=["lexical", "vector"],
        embedder="hash",
        dimension=64,
    )
    assert (snap / "indexes" / "manifest.json").is_file()
    assert man.embedder_name == "hash"
