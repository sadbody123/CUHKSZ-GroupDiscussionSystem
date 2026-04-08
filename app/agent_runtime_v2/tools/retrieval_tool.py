"""Retrieval/indexing tool facade for V2 graph nodes."""

from __future__ import annotations

from pathlib import Path

from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.snapshot_loader import SnapshotBundle, load_snapshot


class RetrievalTool:
    def load_bundle(self, snapshot_dir: str) -> SnapshotBundle:
        return load_snapshot(Path(snapshot_dir).resolve())

    def build_role_router(self, bundle: SnapshotBundle) -> RoleRouter:
        ped, top, ev, doc, _src = build_repositories(bundle)
        return RoleRouter(ped, top, ev, doc, snapshot_dir=bundle.path)
