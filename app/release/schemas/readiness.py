"""Readiness audit schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReadinessCheck(BaseModel):
    check_id: str
    category: str
    severity: str
    passed: bool
    message: str
    suggested_fix: str | None = None
    metadata: dict = Field(default_factory=dict)


class ReadinessReport(BaseModel):
    report_id: str
    profile_id: str
    created_at: str
    overall_status: str
    checks: list[dict] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    recommended_actions: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
