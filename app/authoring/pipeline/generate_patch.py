"""Generate patch proposals pipeline."""

from __future__ import annotations

from app.authoring.schemas.patch import PatchProposal
from app.authoring.store.patch_store import PatchStore


def persist_patches(store: PatchStore, patches: list[PatchProposal]) -> list[PatchProposal]:
    for p in patches:
        store.save_patch(p)
    return patches
