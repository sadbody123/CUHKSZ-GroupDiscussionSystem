"""Eval result schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvalResult(BaseModel):
    suite_id: str | None = None
    case_id: str
    case_type: str
    passed: bool
    score: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
