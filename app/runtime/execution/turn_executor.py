"""Execute user / agent turns."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.runtime.agents.base import append_ai_turn, run_agent_turn
from app.runtime.enums import RoleType
from app.runtime.llm.manager import get_provider
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn
from app.runtime.snapshot_loader import SnapshotBundle, load_snapshot


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TurnExecutor:
    def __init__(self, bundle: SnapshotBundle, session: SessionContext) -> None:
        self.bundle = bundle
        self.session = session
        ped, top, ev, doc, _src = build_repositories(bundle)
        self.router = RoleRouter(ped, top, ev, doc)
        self.profile = resolve_runtime_profile(session.runtime_profile_id)
        self.sm = SessionStateMachine(self.router, orchestration=dict(self.profile.orchestration))
        self.provider = get_provider(session.provider_name)

    @classmethod
    def from_paths(cls, snapshot_dir: Path, session: SessionContext) -> TurnExecutor:
        b = load_snapshot(snapshot_dir.resolve())
        return cls(b, session)

    def submit_user_turn(self, text: str) -> SessionContext:
        tid = f"user-{len(self.session.turns)+1}"
        self.session.turns.append(
            TranscriptTurn(
                turn_id=tid,
                speaker_role=RoleType.USER.value,
                text=text,
                created_at=_utc_now(),
                metadata={},
            )
        )
        return self.session

    def run_next_turn(self) -> tuple[SessionContext, AgentReply | None]:
        last = self.session.turns[-1].speaker_role if self.session.turns else None
        next_role = self.sm.peek_next_role(self.session, last)
        if next_role == RoleType.USER.value:
            return self.session, None
        reply = run_agent_turn(
            router=self.router,
            provider=self.provider,
            role=next_role,
            session=self.session,
        )
        append_ai_turn(self.session, next_role, reply.text)
        return self.session, reply
