"""Release filesystem paths."""

from __future__ import annotations

from pathlib import Path


def bundled_profiles_dir() -> Path:
    return Path(__file__).resolve().parent / "profiles"


def bundled_scenarios_dir() -> Path:
    return Path(__file__).resolve().parent / "scenarios"
