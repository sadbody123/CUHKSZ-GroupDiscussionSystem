"""Session tool reusing existing SessionService manager."""

from __future__ import annotations

from app.application.session_service import SessionService
from app.runtime.schemas.session import SessionContext


class SessionTool:
    def __init__(self, sessions: SessionService) -> None:
        self._sessions = sessions

    def load(self, session_id: str) -> SessionContext | None:
        return self._sessions.manager.load(session_id)

    def save(self, ctx: SessionContext) -> None:
        self._sessions.manager.save(ctx)
