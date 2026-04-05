"""Import a snapshot bundle zip into ``snapshot_root``."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from app.ops.bundles.bundle_manifest import BundleManifest
from app.ops.bundles.checksums import parse_checksums, sha256_file


def _verify_payload(staging: Path) -> BundleManifest:
    mf_path = staging / "bundle_manifest.json"
    if not mf_path.is_file():
        raise ValueError("bundle_manifest.json missing")
    manifest = BundleManifest.model_validate(json.loads(mf_path.read_text(encoding="utf-8")))
    chk_path = staging / "checksums.sha256"
    if not chk_path.is_file():
        raise ValueError("checksums.sha256 missing")
    expected = parse_checksums(chk_path.read_text(encoding="utf-8"))
    for rel, digest in expected.items():
        p = staging.joinpath(*rel.split("/"))
        if not p.is_file():
            raise ValueError(f"missing file in bundle: {rel}")
        if sha256_file(p) != digest:
            raise ValueError(f"checksum mismatch: {rel}")
    return manifest


def import_snapshot_bundle(
    bundle_file: Path,
    snapshot_root: Path,
    *,
    on_conflict: str = "fail",
) -> Path:
    bundle_file = bundle_file.resolve()
    snapshot_root = snapshot_root.resolve()
    snapshot_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        staging = Path(td)
        with zipfile.ZipFile(bundle_file, "r") as zf:
            zf.extractall(staging)
        manifest = _verify_payload(staging)
        snap_src = staging / "snapshot"
        if not snap_src.is_dir():
            raise ValueError("snapshot/ directory missing in bundle")

        base_id = manifest.snapshot_id
        target = snapshot_root / base_id

        if target.exists():
            if on_conflict == "fail":
                raise FileExistsError(f"snapshot already exists: {target}")
            if on_conflict == "overwrite":
                shutil.rmtree(target)
            elif on_conflict == "rename":
                n = 1
                while (snapshot_root / f"{base_id}__import{n}").exists():
                    n += 1
                base_id = f"{base_id}__import{n}"
                target = snapshot_root / base_id
            else:
                raise ValueError(f"unknown on_conflict: {on_conflict}")

        shutil.copytree(snap_src, target)

    mf_out = target / "manifest.json"
    if mf_out.is_file() and target.name != manifest.snapshot_id:
        raw = json.loads(mf_out.read_text(encoding="utf-8"))
        raw["snapshot_id"] = target.name
        mf_out.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return target
