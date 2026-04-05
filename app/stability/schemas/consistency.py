"""Consistency audit."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConsistencyFinding(BaseModel):
    finding_id: str
    entity_type: str
    entity_id: str | None = None
    check_type: str
    severity: str
    passed: bool
    message: str
    expected: dict | str | None = None
    actual: dict | str | None = None
    suggested_fix: str | None = None
    metadata: dict = Field(default_factory=dict)
