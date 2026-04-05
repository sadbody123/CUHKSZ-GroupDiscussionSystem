"""Filesystem-backed audio assets."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from app.audio.constants import ASSET_AGENT_TTS, ASSET_USER_UPLOAD
from app.audio.schemas.audio import AudioAssetRecord


class AudioStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def session_dir(self, session_id: str) -> Path:
        return self._root / session_id

    def _manifest_path(self, asset_id: str) -> Path:
        return self._root / "_manifests" / f"{asset_id}.json"

    def save_bytes(
        self,
        *,
        session_id: str,
        data: bytes,
        file_name: str,
        asset_kind: str,
        mime_type: str,
        provider_name: str | None,
        transcript_text: str | None = None,
        turn_id: str | None = None,
        extra_meta: dict[str, Any] | None = None,
    ) -> AudioAssetRecord:
        aid = str(uuid.uuid4())
        sub = "uploads" if asset_kind in (ASSET_USER_UPLOAD, "user_transcription_source") else "synthesized"
        rel_dir = self.session_dir(session_id) / sub
        rel_dir.mkdir(parents=True, exist_ok=True)
        safe_name = file_name.replace("..", "_").replace("/", "_")
        dest = rel_dir / f"{aid}_{safe_name}"
        dest.write_bytes(data)
        rec = AudioAssetRecord(
            asset_id=aid,
            session_id=session_id,
            turn_id=turn_id,
            asset_kind=asset_kind,
            file_path=str(dest),
            file_name=safe_name,
            mime_type=mime_type,
            size_bytes=len(data),
            duration_ms=None,
            provider_name=provider_name,
            transcript_text=transcript_text,
            metadata={**(extra_meta or {}), "relative": str(dest.relative_to(self._root))},
        )
        man = self._root / "_manifests"
        man.mkdir(parents=True, exist_ok=True)
        (man / f"{aid}.json").write_text(rec.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return rec

    def load_record(self, asset_id: str) -> AudioAssetRecord | None:
        p = self._root / "_manifests" / f"{asset_id}.json"
        if not p.is_file():
            return None
        return AudioAssetRecord.model_validate(json.loads(p.read_text(encoding="utf-8")))

    def read_bytes(self, asset_id: str) -> tuple[bytes, AudioAssetRecord] | None:
        rec = self.load_record(asset_id)
        if not rec:
            return None
        path = Path(rec.file_path)
        if not path.is_file():
            return None
        return path.read_bytes(), rec

    def list_session_assets(self, session_id: str) -> list[AudioAssetRecord]:
        out: list[AudioAssetRecord] = []
        man = self._root / "_manifests"
        if not man.is_dir():
            return out
        for p in sorted(man.glob("*.json")):
            try:
                rec = AudioAssetRecord.model_validate(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            if rec.session_id == session_id:
                out.append(rec)
        return out
