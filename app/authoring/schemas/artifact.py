"""Authorable artifact reference."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuthorableArtifactRef(BaseModel):
    artifact_ref_id: str
    artifact_type: str
    artifact_id: str
    source_type: str
    version: str | None = None
    storage_ref: str | None = None
    derivative_of: str | None = None
    metadata: dict = Field(default_factory=dict)
