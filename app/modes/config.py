"""Resolved paths for mode assets (from ops settings)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.ops.settings import UnifiedSettings, get_ops_settings


def _builtin_modes_package_dir() -> Path:
    return Path(__file__).resolve().parent


@dataclass(frozen=True)
class ModesPaths:
    practice_modes_dir: Path
    presets_dir: Path
    drills_dir: Path
    assessment_templates_dir: Path
    mode_reports_dir: Path


def get_modes_paths(settings: UnifiedSettings | None = None) -> ModesPaths:
    s = settings or get_ops_settings()
    base = getattr(s, "mode_asset_root", None)
    root = Path(base).resolve() if base is not None else _builtin_modes_package_dir()
    return ModesPaths(
        practice_modes_dir=(root / "practice_modes").resolve(),
        presets_dir=(root / "presets").resolve(),
        drills_dir=(root / "drills").resolve(),
        assessment_templates_dir=(root / "assessment_templates").resolve(),
        mode_reports_dir=s.mode_reports_dir.resolve(),
    )
