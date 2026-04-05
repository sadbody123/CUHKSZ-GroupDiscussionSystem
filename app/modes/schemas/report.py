"""ModeSessionReport schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ModeSessionReport(BaseModel):
    report_id: str
    session_id: str
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    created_at: str = ""
    phase_progress: dict[str, Any] = Field(default_factory=dict)
    timer_events: list[dict[str, Any]] = Field(default_factory=list)
    constraint_events: list[dict[str, Any]] = Field(default_factory=list)
    success_checks: list[dict[str, Any]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_next_actions: list[str] = Field(default_factory=list)
    proxy_notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
