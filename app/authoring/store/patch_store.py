"""Patch proposal store."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.authoring.schemas.patch import PatchProposal

_SAFE = re.compile(r"^[\w.\-]+$")


class PatchStore:
    def __init__(self, patches_dir: Path) -> None:
        self._dir = patches_dir.resolve()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, patch_id: str) -> Path:
        if not _SAFE.match(patch_id):
            raise ValueError("invalid patch_id")
        return self._dir / f"{patch_id}.json"

    def save_patch(self, patch: PatchProposal) -> Path:
        p = self._path(patch.patch_id)
        p.write_text(json.dumps(patch.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_patch(self, patch_id: str) -> PatchProposal | None:
        p = self._path(patch_id)
        if not p.is_file():
            return None
        return PatchProposal.model_validate_json(p.read_text(encoding="utf-8"))

    def list_patches(self) -> list[PatchProposal]:
        out: list[PatchProposal] = []
        for f in sorted(self._dir.glob("*.json")):
            try:
                out.append(PatchProposal.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out

    def update_patch_status(self, patch_id: str, status: str) -> bool:
        p = self.load_patch(patch_id)
        if not p:
            return False
        p.status = status
        self.save_patch(p)
        return True
