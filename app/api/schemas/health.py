"""Health check."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    default_provider: str
    default_snapshot_dir: str = Field(description="Resolved snapshot root on server")
