"""Participant specs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParticipantSpec(BaseModel):
    participant_id: str
    display_name: str = ""
    seat_label: str = ""
    team_id: str = ""
    stance: str = ""
    controller_type: str = "agent"  # user / agent / system
    relation_to_user: str = "neutral"  # self / ally / opponent / neutral
    persona_tags: list[str] = Field(default_factory=list)
    intro_priority: int | None = None
    summary_priority: int | None = None
    can_interrupt: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
