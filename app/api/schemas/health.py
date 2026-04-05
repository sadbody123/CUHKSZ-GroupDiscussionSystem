"""Health check."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    default_provider: str
    default_snapshot_dir: str = Field(description="Resolved snapshot root on server")
    app_env: str = "development"
    app_version: str = ""
    default_runtime_profile: str = "default"
    request_id: str | None = None
