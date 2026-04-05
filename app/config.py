"""Application configuration from environment with safe defaults."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from app.ops.settings import get_ops_settings


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    """Runtime settings for offline build (delegates paths/numeric to unified ops settings)."""

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
        o = get_ops_settings()
        return cls(
            project_root=o.project_root.resolve(),
            snapshot_root=o.snapshot_root.resolve(),
            chunk_size=o.chunk_size,
            chunk_overlap=o.chunk_overlap,
            min_text_chars=o.min_text_chars,
            log_level=o.log_level,
        )


def get_settings() -> Settings:
    return Settings.from_env()
