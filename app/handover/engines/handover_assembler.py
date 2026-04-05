"""Assemble handover kit directory."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.handover.schemas.handover import HandoverKitManifest


def assemble_handover_kit(
    output_dir: Path,
    *,
    profile_id: str,
    manifest_path: Path,
    bom_path: Path,
    demo_kit_path: Path | None,
    acceptance_path: Path,
    verification_path: Path,
    docs_bundle_paths: list[str],
) -> HandoverKitManifest:
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    hid = f"hk_{uuid.uuid4().hex[:10]}"

    def _copy(src: Path, name: str) -> None:
        if src.is_file():
            shutil.copy2(src, output_dir / name)

    _copy(manifest_path, "release_manifest.json")
    _copy(bom_path, "bill_of_materials.json")
    _copy(acceptance_path, "acceptance_evidence.json")
    _copy(verification_path, "delivery_verification.json")
    if demo_kit_path and demo_kit_path.is_dir():
        dest = output_dir / "demo_kit"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(demo_kit_path, dest)

    hm = HandoverKitManifest(
        handover_kit_id=hid,
        release_id=f"rel_{profile_id}",
        created_at=now,
        target_audience="local_operator",
        release_manifest_ref="release_manifest.json",
        bom_ref="bill_of_materials.json",
        demo_kit_ref="demo_kit/" if demo_kit_path else None,
        acceptance_evidence_ref="acceptance_evidence.json",
        docs_refs=docs_bundle_paths,
        script_refs=["scripts/verify_handover.sh", "scripts/run_final_demo.sh"],
        included_output_paths={"root": "handover_kit"},
        notes=[
            "This kit is for local review and course handover — not a cloud deployment package.",
            "Known limitations are listed in acceptance_evidence and KNOWN_LIMITATIONS_FINAL.md.",
        ],
        metadata={},
    )
    (output_dir / "handover_kit_manifest.json").write_text(
        json.dumps(hm.model_dump(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return hm
