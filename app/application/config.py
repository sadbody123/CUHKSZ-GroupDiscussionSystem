"""Application-layer configuration (API / UI / services)."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field

from app.config import get_settings


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


class AppConfig(BaseModel):
    """Settings for service layer, distinct from offline build `Settings`."""

    project_root: Path = Field(default_factory=_project_root)
    snapshot_root: Path
    session_storage_dir: Path
    default_provider: str = "mock"
    default_model: str | None = None
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    ui_api_base_url: str = "http://127.0.0.1:8000"

    @classmethod
    def from_env(cls) -> AppConfig:
        root = _project_root()
        base = get_settings()
        snap = base.snapshot_root
        session_dir = os.environ.get("SESSION_STORAGE_DIR")
        storage = Path(session_dir).resolve() if session_dir else root / "storage" / "sessions"
        return cls(
            project_root=root,
            snapshot_root=snap,
            session_storage_dir=storage,
            default_provider=os.environ.get("DEFAULT_PROVIDER", "mock"),
            default_model=os.environ.get("DEFAULT_MODEL"),
            api_host=os.environ.get("API_HOST", "127.0.0.1"),
            api_port=int(os.environ.get("API_PORT", "8000")),
            ui_api_base_url=os.environ.get("UI_API_BASE_URL", "http://127.0.0.1:8000"),
        )


def get_app_config() -> AppConfig:
    return AppConfig.from_env()
