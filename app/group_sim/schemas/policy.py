"""Seat policy."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SeatPolicy(BaseModel):
    participant_id: str
    supportiveness: float | None = None
    challenge_level: float | None = None
    elaboration_level: float | None = None
    interruption_style: str | None = None  # conservative / balanced / aggressive
    target_turn_share: float | None = None
    max_consecutive_turns: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
