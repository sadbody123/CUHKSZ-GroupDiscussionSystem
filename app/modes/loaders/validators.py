"""Light validation helpers."""

from __future__ import annotations

from app.modes.constants import DEFAULT_MODE_ID
from app.modes.loaders.yaml_loader import get_mode_registry


def ensure_mode_exists(mode_id: str) -> bool:
    return mode_id in get_mode_registry().modes


def default_mode_id() -> str:
    reg = get_mode_registry()
    return DEFAULT_MODE_ID if DEFAULT_MODE_ID in reg.modes else (next(iter(reg.modes.keys())) if reg.modes else DEFAULT_MODE_ID)
