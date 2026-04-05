"""Reviewer profile schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewerProfile(BaseModel):
    reviewer_id: str
    display_name: str
    role_title: str | None = None
    created_at: str
    preferred_rubric_id: str | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
