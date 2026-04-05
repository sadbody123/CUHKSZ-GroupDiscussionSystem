"""Session-level aggregated speech report."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionSpeechReport(BaseModel):
    report_id: str
    session_id: str
    turn_analysis_ids: list[str] = Field(default_factory=list)
    aggregate_metrics: dict[str, Any] = Field(default_factory=dict)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    proxy_disclaimer: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
