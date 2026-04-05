"""Bill of materials from registry + docs."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.handover.schemas.bom import BillOfMaterials, BillOfMaterialsEntry
from app.handover.config import project_root
from app.ops.artifacts.registry import ArtifactRegistry


def _checksum_file(p: Path, max_bytes: int = 2_000_000) -> str | None:
    if not p.is_file() or p.stat().st_size > max_bytes:
        return None
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()[:16]


def build_bom(
    profile_id: str,
    *,
    extra_doc_paths: list[Path] | None = None,
) -> BillOfMaterials:
    now = datetime.now(timezone.utc).isoformat()
    bom_id = f"bom_{profile_id}_{uuid.uuid4().hex[:8]}"
    entries: list[BillOfMaterialsEntry] = []
    warnings: list[str] = []
    reg = ArtifactRegistry()
    try:
        rows = reg.scan_known_dirs()[:200]
    except OSError as e:
        warnings.append(str(e))
        rows = []
    for i, r in enumerate(rows):
        rel = r.path
        p = Path(rel)
        st = "missing" if not p.is_file() and not p.is_dir() else "ok"
        entries.append(
            BillOfMaterialsEntry(
                bom_item_id=f"art_{i}_{r.artifact_kind}",
                kind=r.artifact_kind,
                ref_id=r.artifact_id,
                path=str(p.name),
                checksum=_checksum_file(p) if p.is_file() else None,
                required_for_demo=False,
                required_for_handover=r.artifact_kind in ("snapshot", "readiness_report", "demo_bundle"),
                status=st,
                metadata={"artifact_kind": r.artifact_kind},
            )
        )
    root = project_root()
    for name, rel, kind, demo, ho in [
        ("README.md", root / "README.md", "docs", True, True),
        ("QUICKSTART.md", root / "QUICKSTART.md", "docs", True, True),
        ("main.py", root / "main.py", "script", False, True),
    ]:
        st = "ok" if rel.is_file() else "missing"
        if st == "missing":
            warnings.append(f"expected file missing: {name}")
        entries.append(
            BillOfMaterialsEntry(
                bom_item_id=f"doc_{name}",
                kind=kind,
                ref_id=name,
                path=name,
                required_for_demo=demo,
                required_for_handover=ho,
                status=st,
            )
        )
    for p in extra_doc_paths or []:
        if p.is_file():
            entries.append(
                BillOfMaterialsEntry(
                    bom_item_id=f"extra_{p.stem}",
                    kind="docs",
                    ref_id=p.stem,
                    path=p.name,
                    required_for_demo=False,
                    required_for_handover=True,
                    status="ok",
                )
            )
    return BillOfMaterials(
        bom_id=bom_id,
        profile_id=profile_id,
        created_at=now,
        entries=entries,
        warnings=warnings,
        metadata={},
    )
