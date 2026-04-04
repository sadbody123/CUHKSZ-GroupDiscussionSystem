"""Turn / discussion API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SubmitUserTurnRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=32000)


class SubmitUserTurnResponse(BaseModel):
    session_id: str
    turn_count: int
    new_turn: dict[str, Any]


class RunNextTurnResponse(BaseModel):
    next_role: str
    generated_reply: str | None = None
    generated_role: str | None = None
    updated_phase: str
    turn_count: int
    reply_metadata: dict[str, Any] = Field(default_factory=dict)


class AutoRunRequest(BaseModel):
    max_steps: int = Field(4, ge=1, le=32)


class AutoRunResponse(BaseModel):
    new_turns: list[dict[str, Any]]
    session: dict[str, Any]
