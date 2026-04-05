"""Ops schemas (artifacts, etc.)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ArtifactRecord(BaseModel):
    artifact_id: str
    artifact_kind: str
    path: str
    created_at: str = ""
    size_bytes: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
