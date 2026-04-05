"""Optional OpenAI-compatible transcription (HTTP)."""

from __future__ import annotations

import os

import httpx

from app.audio.providers.asr_base import BaseASRProvider
from app.audio.schemas.asr import TranscriptionRequest, TranscriptionResponse


class OpenAIWhisperCompatibleProvider(BaseASRProvider):
    name = "openai_whisper"

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.environ.get("OPENAI_TRANSCRIBE_MODEL") or "whisper-1"
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY required for OpenAIWhisperCompatibleProvider")

    def transcribe(self, request: TranscriptionRequest) -> TranscriptionResponse:
        url = f"{self.base_url}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if request.file_path:
            from pathlib import Path

            data_bytes = Path(request.file_path).read_bytes()
            files = {"file": ("audio.wav", data_bytes, request.mime_type or "audio/wav")}
        elif request.audio_bytes:
            files = {"file": ("audio.wav", request.audio_bytes, request.mime_type or "audio/wav")}
        else:
            raise ValueError("file_path or audio_bytes required")
        data = {"model": self.model}
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, headers=headers, data=data, files=files)
            r.raise_for_status()
            out = r.json()
        txt = out.get("text") or ""
        return TranscriptionResponse(
            provider_name=self.name,
            text=txt,
            language=out.get("language"),
            raw=out,
            metadata={},
        )
