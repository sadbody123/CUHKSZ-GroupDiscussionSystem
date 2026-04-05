"""Load builtin curriculum packs from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.curriculum.loaders.validators import validate_pack_refs
from app.curriculum.schemas.pack import CurriculumPack


def _packs_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "packs"


def load_yaml_pack(path: Path) -> CurriculumPack:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    pack = CurriculumPack.model_validate(raw)
    validate_pack_refs(pack)
    return pack


def load_builtin_pack(pack_id: str) -> CurriculumPack | None:
    p = _packs_dir() / f"{pack_id}.yaml"
    if not p.is_file():
        return None
    return load_yaml_pack(p)


def list_builtin_pack_ids() -> list[str]:
    out: list[str] = []
    for f in sorted(_packs_dir().glob("*.yaml")):
        out.append(f.stem)
    return out


def load_all_builtin_packs() -> dict[str, CurriculumPack]:
    out: dict[str, CurriculumPack] = {}
    for pid in list_builtin_pack_ids():
        pk = load_builtin_pack(pid)
        if pk:
            out[pid] = pk
    return out
