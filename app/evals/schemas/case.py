"""Eval case schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    case_id: str
    case_type: str
    description: str | None = None
    snapshot_id: str | None = None
    topic_id: str | None = None
    runtime_profile_id: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
