"""Authoring draft."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuthoringDraft(BaseModel):
    draft_id: str
    artifact_type: str
    artifact_id: str
    title: str | None = None
    author_id: str | None = None
    base_artifact_ref_id: str | None = None
    base_version: str | None = None
    derivative_of: str | None = None
    status: str = "draft"
    created_at: str
    updated_at: str | None = None
    content: dict = Field(default_factory=dict)
    change_summary: list[str] = Field(default_factory=list)
    linked_patch_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
