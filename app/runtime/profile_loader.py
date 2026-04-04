"""Load runtime profile YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.runtime.schemas.profile import RuntimeProfile

_PROFILE_DIR = Path(__file__).resolve().parent / "profiles"


def profiles_directory() -> Path:
    return _PROFILE_DIR


def list_profile_ids() -> list[str]:
    if not _PROFILE_DIR.is_dir():
        return []
    out: list[str] = []
    for p in sorted(_PROFILE_DIR.glob("*.yaml")):
        out.append(p.stem)
    return out


def load_profile_yaml(profile_id: str) -> dict:
    """Load raw YAML for ``profile_id`` (filename stem)."""
    safe = profile_id.replace("/", "").replace("\\", "")
    path = _PROFILE_DIR / f"{safe}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Profile not found: {profile_id}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid profile YAML: {profile_id}")
    raw.setdefault("profile_id", safe)
    return raw


def load_profile_model(profile_id: str) -> RuntimeProfile:
    raw = load_profile_yaml(profile_id)
    return RuntimeProfile.model_validate(raw)
