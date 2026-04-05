"""Facade for snapshot bundle export / import."""

from __future__ import annotations

from pathlib import Path

from app.ops.bundles.bundle_manifest import BundleManifest
from app.ops.bundles.snapshot_exporter import export_snapshot_bundle as _export
from app.ops.bundles.snapshot_importer import import_snapshot_bundle as _import
from app.ops.settings import UnifiedSettings, get_ops_settings


def export_snapshot_bundle(
    *,
    snapshot_dir: Path | None = None,
    snapshot_id: str | None = None,
    output_file: Path,
    settings: UnifiedSettings | None = None,
) -> tuple[Path, BundleManifest]:
    s = settings or get_ops_settings()
    if snapshot_dir is not None:
        d = snapshot_dir.resolve()
    elif snapshot_id:
        d = (s.snapshot_root / snapshot_id).resolve()
        if not d.is_dir():
            raise FileNotFoundError(f"snapshot not found: {snapshot_id}")
    else:
        raise ValueError("specify snapshot_dir or snapshot_id")
    return _export(d, output_file)


def import_snapshot_bundle(
    bundle_file: Path,
    *,
    on_conflict: str = "fail",
    settings: UnifiedSettings | None = None,
) -> Path:
    s = settings or get_ops_settings()
    return _import(bundle_file, s.snapshot_root, on_conflict=on_conflict)
