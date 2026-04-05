"""Snapshot bundle export/import."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2

from app.ops.bundles.bundle_manager import export_snapshot_bundle, import_snapshot_bundle
from app.ops.settings import get_ops_settings
from app.runtime.snapshot_loader import load_snapshot


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_bundle_export_import_roundtrip(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    snap_root = tmp_path / "snapshots"
    snap_root.mkdir()
    monkeypatch.setenv("SNAPSHOT_ROOT", str(snap_root))
    get_ops_settings.cache_clear()

    z = tmp_path / "out.zip"
    export_snapshot_bundle(snapshot_dir=SNAPSHOT_V2, output_file=z)

    import_snapshot_bundle(z, on_conflict="fail")

    b = load_snapshot(snap_root / "dev_snapshot_v2")
    assert b.manifest.snapshot_id == "dev_snapshot_v2"
