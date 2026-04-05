"""Preview sandbox schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PreviewSpec(BaseModel):
    preview_id: str
    draft_id: str
    preview_kind: str
    snapshot_id: str | None = None
    learner_id: str | None = None
    provider_name: str | None = None
    inputs: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class PreviewResult(BaseModel):
    preview_result_id: str
    draft_id: str
    preview_id: str
    preview_kind: str
    created_at: str
    success: bool
    summary: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    generated_refs: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
