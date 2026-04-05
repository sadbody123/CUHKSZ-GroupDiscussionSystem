"""List and inspect local offline snapshots."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.application.config import AppConfig
from app.application.dto import SnapshotListItemDTO
from app.application.exceptions import SnapshotNotFoundError
from app.offline_build.build_snapshot.validators import validate_snapshot_dir
from app.indexing.schemas.index_manifest import IndexManifest
from app.runtime.snapshot_loader import load_snapshot

_SAFE_ID = re.compile(r"^[\w.\-]+$")


class SnapshotService:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def resolve_snapshot_dir(self, snapshot_id: str) -> Path:
        if not _SAFE_ID.match(snapshot_id):
            raise SnapshotNotFoundError(f"Invalid snapshot_id: {snapshot_id!r}")
        root = self._config.snapshot_root.resolve()
        p = (self._config.snapshot_root / snapshot_id).resolve()
        try:
            rel = p.relative_to(root)
        except ValueError as e:
            raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_id}") from e
        if len(rel.parts) != 1 or not p.is_dir() or not (p / "manifest.json").is_file():
            raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_id}")
        return p

    def list_snapshots(self) -> list[SnapshotListItemDTO]:
        root = self._config.snapshot_root
        if not root.is_dir():
            return []
        out: list[SnapshotListItemDTO] = []
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            mf = child / "manifest.json"
            if not mf.is_file():
                continue
            try:
                raw = json.loads(mf.read_text(encoding="utf-8"))
                # Folder name is the canonical id for paths under snapshot_root.
                sid = child.name
                out.append(
                    SnapshotListItemDTO(
                        snapshot_id=sid,
                        schema_version=str(raw.get("schema_version", "1.0")),
                        created_at=str(raw.get("created_at", "")),
                        topic_card_count=int(raw.get("topic_card_count", 0)),
                        evidence_index_count=int(raw.get("evidence_index_count", 0)),
                        pedagogy_item_count=int(raw.get("pedagogy_item_count", 0)),
                        available=True,
                    )
                )
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
        return out

    def validate_usable(self, snapshot_dir: Path) -> bool:
        res = validate_snapshot_dir(snapshot_dir)
        return res.ok

    def get_snapshot_bundle_summary(self, snapshot_id: str) -> dict:
        path = self.resolve_snapshot_dir(snapshot_id)
        b = load_snapshot(path)
        m = b.manifest.model_dump()
        br = b.build_report.model_dump()
        return {
            "snapshot_id": b.manifest.snapshot_id,
            "path": str(path),
            "manifest": m,
            "build_report": br,
            "counts": {
                "topic_cards": len(b.topic_cards),
                "pedagogy_items": len(b.pedagogy_items),
                "evidence_index": len(b.evidence_index),
                "normalized_docs": len(b.normalized_docs),
                "evidence_chunks": len(b.evidence_chunks),
            },
            "validation_ok": self.validate_usable(path),
        }

    def get_index_status(self, snapshot_id: str) -> dict:
        path = self.resolve_snapshot_dir(snapshot_id)
        mf = path / "indexes" / "manifest.json"
        if not mf.is_file():
            return {
                "snapshot_id": snapshot_id,
                "has_indexes": False,
                "available_modes": [],
                "stores": [],
                "embedder_name": None,
                "dimension": None,
                "item_counts": {},
            }
        man = IndexManifest.model_validate(json.loads(mf.read_text(encoding="utf-8")))
        return {
            "snapshot_id": snapshot_id,
            "has_indexes": True,
            "available_modes": list(man.available_modes),
            "stores": list(man.stores),
            "embedder_name": man.embedder_name,
            "dimension": man.dimension,
            "item_counts": dict(man.item_counts),
        }
