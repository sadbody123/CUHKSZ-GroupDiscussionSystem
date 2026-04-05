"""Load release profile YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.release.config import bundled_profiles_dir
from app.release.schemas.profile import ReleaseProfile


def load_release_profile(profile_id: str, *, search_dirs: list[Path] | None = None) -> ReleaseProfile:
    from app.ops.settings import get_ops_settings

    s = get_ops_settings()
    dirs: list[Path] = []
    rd = getattr(s, "release_profile_dir", None)
    if rd:
        dirs.append(Path(rd).resolve())
    dirs.append(bundled_profiles_dir())
    name = f"{profile_id}.yaml"
    for d in dirs:
        p = d / name
        if p.is_file():
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            raw.setdefault("profile_id", profile_id)
            return ReleaseProfile.model_validate(raw)
    raise FileNotFoundError(f"release profile not found: {profile_id}")


def list_profile_ids(search_dirs: list[Path] | None = None) -> list[str]:
    from app.ops.settings import get_ops_settings

    s = get_ops_settings()
    seen: set[str] = set()
    out: list[str] = []
    dirs: list[Path] = [bundled_profiles_dir()]
    rd = getattr(s, "release_profile_dir", None)
    if rd:
        dirs.insert(0, Path(rd).resolve())
    for d in dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.yaml")):
            if f.stem not in seen:
                seen.add(f.stem)
                out.append(f.stem)
    return sorted(out)
