"""In-memory session store with optional JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path

from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionContext] = {}

    def upsert(self, ctx: SessionContext) -> None:
        self._sessions[ctx.session_id] = ctx

    def get(self, session_id: str) -> SessionContext | None:
        return self._sessions.get(session_id)

    def save_json(self, path: Path, session_id: str) -> None:
        ctx = self.get(session_id)
        if not ctx:
            return
        data = ctx.model_dump()
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def load_transcript_file(path: Path) -> tuple[str, str | None, list[TranscriptTurn]]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        sid = str(raw.get("session_id", "session"))
        tid = raw.get("topic_id")
        turns_raw = raw.get("turns") or []
        turns = [TranscriptTurn.model_validate(x) for x in turns_raw]
        return sid, str(tid) if tid else None, turns
