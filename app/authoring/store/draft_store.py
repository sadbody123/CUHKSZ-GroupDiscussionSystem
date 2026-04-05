"""Draft filesystem store."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.authoring.schemas.draft import AuthoringDraft

_SAFE = re.compile(r"^[\w.\-]+$")


class DraftStore:
    def __init__(self, drafts_dir: Path) -> None:
        self._dir = drafts_dir.resolve()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, draft_id: str) -> Path:
        if not _SAFE.match(draft_id):
            raise ValueError("invalid draft_id")
        return self._dir / f"{draft_id}.json"

    def create_draft(self, draft: AuthoringDraft) -> Path:
        p = self._path(draft.draft_id)
        if p.is_file():
            raise ValueError(f"draft already exists: {draft.draft_id}")
        p.write_text(json.dumps(draft.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def save_draft(self, draft: AuthoringDraft) -> Path:
        p = self._path(draft.draft_id)
        p.write_text(json.dumps(draft.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_draft(self, draft_id: str) -> AuthoringDraft | None:
        p = self._path(draft_id)
        if not p.is_file():
            return None
        return AuthoringDraft.model_validate_json(p.read_text(encoding="utf-8"))

    def list_drafts(self) -> list[AuthoringDraft]:
        out: list[AuthoringDraft] = []
        for f in sorted(self._dir.glob("*.json")):
            try:
                out.append(AuthoringDraft.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out

    def archive_draft(self, draft_id: str) -> bool:
        d = self.load_draft(draft_id)
        if not d:
            return False
        d.status = "archived"
        from datetime import datetime, timezone

        d.updated_at = datetime.now(timezone.utc).isoformat()
        self.save_draft(d)
        return True
