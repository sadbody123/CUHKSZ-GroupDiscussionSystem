"""Eval report schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvalReport(BaseModel):
    report_id: str
    created_at: str
    suite_id: str | None = None
    profile_ids: list[str] = Field(default_factory=list)
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    summary: dict[str, Any] = Field(default_factory=dict)
    results: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
