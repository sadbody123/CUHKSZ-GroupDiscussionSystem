"""High-level session CRUD."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.runtime.schemas.session import SessionContext
from app.runtime.session.file_store import FileSessionStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionManager:
    def __init__(self, store: FileSessionStore | None = None) -> None:
        self.store = store or FileSessionStore()

    def create_session(
        self,
        *,
        topic_id: str,
        snapshot_dir: str,
        user_stance: str | None = None,
        provider_name: str = "mock",
        model_name: str | None = None,
        phase: str = "discussion",
        max_discussion_turns: int | None = None,
        runtime_profile_id: str | None = None,
        created_with: str = "cli",
    ) -> SessionContext:
        sid = str(uuid.uuid4())
        ctx = SessionContext(
            session_id=sid,
            topic_id=topic_id,
            user_stance=user_stance,
            phase=phase,
            max_discussion_turns=max_discussion_turns,
            provider_name=provider_name,
            model_name=model_name,
            snapshot_dir=snapshot_dir,
            runtime_profile_id=(runtime_profile_id or "default"),
            metadata={
                "created_with": created_with,
                "created_at": _utc_now(),
            },
        )
        self.store.save(ctx)
        return ctx

    def load(self, session_id: str) -> SessionContext | None:
        return self.store.load(session_id)

    def save(self, ctx: SessionContext) -> None:
        self.store.save(ctx)
