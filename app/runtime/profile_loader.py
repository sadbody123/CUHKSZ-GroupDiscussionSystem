"""Load runtime profile YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.runtime.schemas.profile import RuntimeProfile

_PROFILE_DIR = Path(__file__).resolve().parent / "profiles"


def _published_dir() -> Path | None:
    try:
        from app.ops.settings import get_ops_settings

        s = get_ops_settings()
        d = getattr(s, "authoring_root_dir", None)
        if d is None:
            return None
        p = Path(d).resolve() / "published" / "runtime_profiles"
        return p if p.is_dir() else None
    except Exception:
        return None


def profiles_directory() -> Path:
    return _PROFILE_DIR


def list_profile_ids() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    if _PROFILE_DIR.is_dir():
        for p in sorted(_PROFILE_DIR.glob("*.yaml")):
            seen.add(p.stem)
            out.append(p.stem)
    pub = _published_dir()
    if pub:
        for p in sorted(pub.glob("*.yaml")):
            if p.stem not in seen:
                seen.add(p.stem)
                out.append(p.stem)
    return sorted(out)


def load_profile_yaml(profile_id: str) -> dict:
    """Load raw YAML for ``profile_id`` (filename stem). Builtin first, then authoring published."""
    safe = profile_id.replace("/", "").replace("\\", "")
    path = _PROFILE_DIR / f"{safe}.yaml"
    if not path.is_file():
        pub = _published_dir()
        if pub:
            alt = pub / f"{safe}.yaml"
            if alt.is_file():
                path = alt
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
