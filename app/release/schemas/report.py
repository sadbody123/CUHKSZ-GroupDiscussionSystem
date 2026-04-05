"""Scope freeze / reports."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScopeDecision(BaseModel):
    decision_id: str
    capability_id: str
    decision: str
    reason: str
    impact: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ScopeFreezeSummary(BaseModel):
    profile_id: str
    generated_at: str
    decisions: list[ScopeDecision] = Field(default_factory=list)
    summary_text: str = ""
    metadata: dict = Field(default_factory=dict)
