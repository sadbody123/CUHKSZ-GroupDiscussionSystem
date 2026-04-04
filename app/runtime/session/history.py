"""Transcript helpers."""

from __future__ import annotations

from app.runtime.schemas.session import SessionContext


def recent_turns(session: SessionContext, n: int = 5):
    return session.turns[-n:]
