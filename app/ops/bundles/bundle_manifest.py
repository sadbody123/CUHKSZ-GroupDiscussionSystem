"""Bundle manifest schema (zip root)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BundleManifest(BaseModel):
    bundle_id: str
    created_at: str
    app_version: str
    snapshot_id: str
    schema_version: str = "1.0"
    included_files: list[str] = Field(default_factory=list)
    checksums: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
