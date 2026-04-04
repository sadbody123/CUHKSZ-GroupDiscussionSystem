"""JSON file persistence for sessions."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.runtime.schemas.session import SessionContext

_SAFE = re.compile(r"^[\w.\-]+$")


def default_storage_root() -> Path:
    return Path(__file__).resolve().parents[3] / "storage" / "sessions"


class FileSessionStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or default_storage_root()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        if not _SAFE.match(session_id):
            raise ValueError("Invalid session_id")
        return self.root / f"{session_id}.json"

    def save(self, ctx: SessionContext) -> None:
        p = self._path(ctx.session_id)
        p.write_text(ctx.model_dump_json(indent=2) + "\n", encoding="utf-8")

    def load(self, session_id: str) -> SessionContext | None:
        p = self._path(session_id)
        if not p.is_file():
            return None
        return SessionContext.model_validate_json(p.read_text(encoding="utf-8"))

    def list_session_ids(self) -> list[str]:
        return sorted([x.stem for x in self.root.glob("*.json")])
