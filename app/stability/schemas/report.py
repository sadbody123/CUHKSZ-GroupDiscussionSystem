"""Stability report."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StabilityReport(BaseModel):
    report_id: str
    created_at: str
    profile_id: str | None = None
    overall_status: str
    consistency_summary: dict = Field(default_factory=dict)
    e2e_summary: dict = Field(default_factory=dict)
    issue_summary: dict = Field(default_factory=dict)
    known_limitations: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
