"""Turn statistics."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParticipantTurnStats(BaseModel):
    participant_id: str
    turn_count: int = 0
    total_chars: int = 0
    avg_chars_per_turn: float | None = None
    phase_counts: dict[str, int] = Field(default_factory=dict)
    interruption_count: int = 0
    linked_argument_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TeamTurnStats(BaseModel):
    team_id: str
    turn_count: int = 0
    total_chars: int = 0
    intro_done: bool = False
    summary_done: bool = False
    discussion_turns: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
