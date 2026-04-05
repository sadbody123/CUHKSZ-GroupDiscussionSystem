"""Group balance / simulation report."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GroupBalanceReport(BaseModel):
    report_id: str
    session_id: str
    roster_template_id: str | None = None
    created_at: str = ""
    participant_stats: list[dict[str, Any]] = Field(default_factory=list)
    team_stats: list[dict[str, Any]] = Field(default_factory=list)
    balance_flags: list[dict[str, Any]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
