"""Curriculum pack filesystem store (builtin YAML + custom JSON)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.curriculum.loaders.yaml_loader import load_builtin_pack, list_builtin_pack_ids
from app.curriculum.schemas.pack import CurriculumPack

_SAFE = re.compile(r"^[\w.\-]+$")


class PackStore:
    def __init__(self, builtin_dir: Path, custom_dir: Path) -> None:
        self._builtin = builtin_dir
        self._custom = custom_dir.resolve()
        self._custom.mkdir(parents=True, exist_ok=True)

    def load_pack(self, pack_id: str) -> CurriculumPack | None:
        if not _SAFE.match(pack_id):
            raise ValueError("invalid pack_id")
        c = self._custom / f"{pack_id}.json"
        if c.is_file():
            return CurriculumPack.model_validate_json(c.read_text(encoding="utf-8"))
        return load_builtin_pack(pack_id)

    def save_custom_pack(self, pack: CurriculumPack) -> Path:
        if not _SAFE.match(pack.pack_id):
            raise ValueError("invalid pack_id")
        p = self._custom / f"{pack.pack_id}.json"
        p.write_text(json.dumps(pack.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def list_packs(self) -> list[CurriculumPack]:
        seen: dict[str, CurriculumPack] = {}
        for pid in list_builtin_pack_ids():
            pk = load_builtin_pack(pid)
            if pk:
                seen[pid] = pk
        for f in sorted(self._custom.glob("*.json")):
            try:
                pk = CurriculumPack.model_validate_json(f.read_text(encoding="utf-8"))
                seen[pk.pack_id] = pk
            except Exception:
                continue
        return [seen[k] for k in sorted(seen.keys())]
