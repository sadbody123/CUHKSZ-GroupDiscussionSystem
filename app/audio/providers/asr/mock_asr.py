"""Deterministic offline ASR (fixture manifest + byte-hash fallback)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.audio.providers.asr_base import BaseASRProvider
from app.audio.schemas.asr import TranscriptionRequest, TranscriptionResponse


class MockASRProvider(BaseASRProvider):
    name = "mock_asr"

    def __init__(self, manifest_path: Path | None = None) -> None:
        self._map: dict[str, str] = {}
        p = manifest_path
        if p and p.is_file():
            raw = json.loads(p.read_text(encoding="utf-8"))
            self._map = {str(k): str(v) for k, v in raw.items()}

    def transcribe(self, request: TranscriptionRequest) -> TranscriptionResponse:
        text = str(self._map.get("default", "mock ASR default transcript"))
        if request.file_path:
            base = Path(request.file_path).name
            text = self._map.get(base, text)
        elif request.audio_bytes:
            h = hashlib.sha256(request.audio_bytes).hexdigest()[:12]
            text = self._map.get(f"bytes:{h}", f"mock transcript bytes:{h}")
        return TranscriptionResponse(
            provider_name=self.name,
            text=text,
            language=request.language_hint or "en",
            confidence=0.99,
            raw={"mock": True},
            metadata=dict(request.metadata),
        )
