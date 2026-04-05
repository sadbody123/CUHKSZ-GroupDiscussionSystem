"""Rule-based delivery signals."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DeliverySignal(BaseModel):
    signal_id: str
    signal_type: str
    severity: str
    message: str
    metric_name: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
