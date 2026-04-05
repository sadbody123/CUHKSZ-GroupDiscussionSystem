"""Export a snapshot directory into a portable zip bundle."""

from __future__ import annotations

import json
import shutil
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app.offline_build.build_snapshot.validators import validate_snapshot_dir
from app.ops.bundles.bundle_manifest import BundleManifest
from app.ops.bundles.checksums import sha256_file
from app.ops.version import get_app_version

_EXPECTED_NAMES = [
    "manifest.json",
    "build_report.json",
    "normalized_docs.jsonl",
    "evidence_chunks.jsonl",
    "source_catalog.jsonl",
    "pedagogy_items.jsonl",
    "topic_cards.jsonl",
    "evidence_index.jsonl",
]


def _collect_files(snapshot_dir: Path) -> list[str]:
    out: list[str] = []
    for name in _EXPECTED_NAMES:
        if (snapshot_dir / name).is_file():
            out.append(name)
    idx = snapshot_dir / "indexes"
    if idx.is_dir():
        for p in sorted(idx.rglob("*")):
            if p.is_file():
                out.append(str(p.relative_to(snapshot_dir)).replace("\\", "/"))
    return out


def export_snapshot_bundle(snapshot_dir: Path, output_zip: Path) -> tuple[Path, BundleManifest]:
    snap = snapshot_dir.resolve()
    res = validate_snapshot_dir(snap)
    if not res.ok:
        raise ValueError("snapshot validation failed: " + "; ".join(res.errors[:12]))
    files = _collect_files(snap)
    if not files:
        raise ValueError("no snapshot files found to export")

    mf_raw = json.loads((snap / "manifest.json").read_text(encoding="utf-8"))
    snapshot_id = str(mf_raw.get("snapshot_id") or snap.name)

    with tempfile.TemporaryDirectory() as td:
        staging = Path(td)
        snap_stage = staging / "snapshot"
        snap_stage.mkdir(parents=True)
        rels: list[str] = []
        for rel in files:
            src = snap / rel
            dst = snap_stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            rels.append(f"snapshot/{rel.replace(chr(92), '/')}")

        checksum_map: dict[str, str] = {}
        lines: list[str] = []
        for rel in rels:
            p = staging.joinpath(*rel.split("/"))
            digest = sha256_file(p)
            checksum_map[rel] = digest
            lines.append(f"{digest}  {rel}")
        (staging / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

        manifest = BundleManifest(
            bundle_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            app_version=get_app_version(),
            snapshot_id=snapshot_id,
            schema_version="1.0",
            included_files=["bundle_manifest.json", "checksums.sha256", *rels],
            checksums=checksum_map,
            metadata={
                "exported_from": str(snap),
                "includes_indexes": (snap / "indexes").is_dir(),
            },
        )
        (staging / "bundle_manifest.json").write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")

        output_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(staging.rglob("*")):
                if p.is_file():
                    arc = p.relative_to(staging).as_posix()
                    zf.write(p, arcname=arc)

    return output_zip.resolve(), manifest
