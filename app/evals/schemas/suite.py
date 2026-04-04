"""Eval suite schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvalSuite(BaseModel):
    suite_id: str
    description: str | None = None
    case_refs: list[str] = Field(default_factory=list)
    default_snapshot_id: str | None = None
    default_runtime_profile_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
