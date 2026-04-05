"""Save custom pack."""

from __future__ import annotations

from app.curriculum.schemas.pack import CurriculumPack
from app.curriculum.store.pack_store import PackStore


def publish_custom_pack(store: PackStore, pack: CurriculumPack) -> object:
    return store.save_custom_pack(pack)
