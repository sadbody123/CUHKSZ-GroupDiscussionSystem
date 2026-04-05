"""Role-facing context and turn planning (LLM-ready payloads, no generation here)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RoleContextPacket(BaseModel):
    role: str
    topic_id: str | None = None
    session_phase: str
    topic_card: dict | None = None
    pedagogy_items: list[dict] = Field(default_factory=list)
    evidence_items: list[dict] = Field(default_factory=list)
    used_pedagogy_item_ids: list[str] = Field(default_factory=list)
    used_evidence_ids: list[str] = Field(default_factory=list)
    prompt_template_id: str | None = None
    participant_id: str | None = None
    participant_display_name: str | None = None
    seat_label: str | None = None
    team_id: str | None = None
    relation_to_user: str | None = None
    participant_memory_summary: str | None = None
    team_memory_summary: str | None = None
    roster_context_summary: str | None = None
    metadata: dict = Field(default_factory=dict)


class TurnPlan(BaseModel):
    session_id: str
    phase: str
    next_role: str
    reason: str
    context_packet: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    next_participant_id: str | None = None
    next_team_id: str | None = None
    allocation_reason: str | None = None
    candidate_participant_ids: list[str] = Field(default_factory=list)
