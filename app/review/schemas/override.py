"""Human override decisions (audited, never silent)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OverrideDecision(BaseModel):
    override_id: str
    target_type: str
    target_path: str
    action: str
    new_value: Any = None
    reason: str
    approved: bool = False
    metadata: dict = Field(default_factory=dict)
