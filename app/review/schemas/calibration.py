"""AI vs human calibration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CalibrationResult(BaseModel):
    calibration_id: str
    component_type: str
    component_id: str | None = None
    ai_value: Any = None
    human_value: Any = None
    delta: float | None = None
    agreement_level: str | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class CalibrationReport(BaseModel):
    report_id: str
    review_pack_id: str
    session_id: str
    review_id: str | None = None
    created_at: str
    overall_agreement: str | None = None
    results: list[dict] = Field(default_factory=list)
    key_mismatches: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    reviewed_output_refs: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
