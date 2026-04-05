"""Audio config helpers."""

from __future__ import annotations

from pathlib import Path

from app.ops.settings import get_ops_settings


def audio_storage_root() -> Path:
    return get_ops_settings().audio_storage_dir.resolve()
