"""Resolve curriculum pack by id (builtin or custom)."""

from __future__ import annotations

from app.curriculum.loaders.yaml_loader import load_builtin_pack
from app.curriculum.schemas.pack import CurriculumPack
from app.curriculum.store.pack_store import PackStore


def resolve_pack(store: PackStore, pack_id: str) -> CurriculumPack | None:
    return store.load_pack(pack_id)
