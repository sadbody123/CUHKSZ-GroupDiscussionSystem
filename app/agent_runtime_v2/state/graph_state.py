"""Graph execution control state.

SessionContext remains the source of truth for transcript and business data.
This state only tracks runtime control and intermediate orchestration metadata.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from app.runtime.schemas.session import SessionContext


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DiscussionGraphState(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    runtime_profile_id: str = "default"
    phase: str = "discussion"
    last_role: str | None = None
    next_actor: str | None = None
    loop_index: int = 0
    max_steps: int = 1
    stop_reason: str | None = None
    run_status: str = "running"
    last_successful_node: str | None = None
    runtime_checkpoint_id: str | None = Field(
        default=None,
        validation_alias="checkpoint_id",
        serialization_alias="checkpoint_id",
    )
    trace_id: str | None = None
    emitted_turn_ids: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)
    repair_count: int = 0
    max_repairs: int = 1
    quality_decision: str | None = None
    moderation_action: str | None = None
    interrupt_reason: str | None = None
    review_id: str | None = None
    policy_id: str | None = None
    metadata: dict = Field(default_factory=dict)
    artifacts: dict = Field(default_factory=dict)
    events: list[dict] = Field(default_factory=list)

    @classmethod
    def from_session(
        cls,
        session: SessionContext,
        *,
        run_id: str | None = None,
        max_steps: int = 1,
        trace_id: str | None = None,
        checkpoint_id: str | None = None,
    ) -> "DiscussionGraphState":
        return cls(
            run_id=run_id or str(uuid4()),
            session_id=session.session_id,
            runtime_profile_id=session.runtime_profile_id or "default",
            phase=session.phase or "discussion",
            last_role=(session.turns[-1].speaker_role if session.turns else None),
            max_steps=max_steps,
            trace_id=trace_id,
            runtime_checkpoint_id=checkpoint_id,
            run_status="running",
            metadata={"created_at": _utc_now_iso()},
        )

    def push_event(self, event: dict) -> None:
        self.events.append(event)

    @property
    def checkpoint_id(self) -> str | None:
        return self.runtime_checkpoint_id

    @checkpoint_id.setter
    def checkpoint_id(self, value: str | None) -> None:
        self.runtime_checkpoint_id = value
