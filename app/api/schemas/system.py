"""Public system info (no secrets)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SystemInfoResponse(BaseModel):
    app_name: str
    app_version: str
    app_env: str
    snapshot_root: str
    default_provider: str
    default_runtime_profile: str
    bundle_dir: str
    feature_flags: dict[str, Any] = Field(default_factory=dict)
