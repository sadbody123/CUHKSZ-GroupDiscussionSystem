"""Application configuration from environment with safe defaults."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    """Runtime settings for offline build."""

    project_root: Path = Field(default_factory=_project_root)
    snapshot_root: Path = Field(
        default_factory=lambda: _project_root() / "app" / "knowledge" / "snapshots"
    )
    chunk_size: int = Field(default=600, ge=100, le=8000)
    chunk_overlap: int = Field(default=80, ge=0, le=500)
    min_text_chars: int = Field(default=20, ge=0)
    log_level: str = Field(default="INFO")

    @classmethod
    def from_env(cls) -> "Settings":
        root = _project_root()
        snap = os.environ.get("SNAPSHOT_ROOT")
        snapshot_root = Path(snap).resolve() if snap else root / "app" / "knowledge" / "snapshots"
        return cls(
            project_root=root,
            snapshot_root=snapshot_root,
            chunk_size=int(os.environ.get("CHUNK_SIZE", "600")),
            chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", "80")),
            min_text_chars=int(os.environ.get("MIN_TEXT_CHARS", "20")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )


def get_settings() -> Settings:
    return Settings.from_env()
