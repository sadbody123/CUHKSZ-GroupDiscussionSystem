"""Optional OpenAI-compatible TTS (HTTP)."""

from __future__ import annotations

import os

import httpx

from app.audio.providers.tts_base import BaseTTSProvider
from app.audio.schemas.tts import SynthesisRequest, SynthesisResponse


class OpenAITTSCompatibleProvider(BaseTTSProvider):
    name = "openai_tts"

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.environ.get("OPENAI_TTS_MODEL") or "tts-1"
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY required for OpenAITTSCompatibleProvider")

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        url = f"{self.base_url}/audio/speech"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "input": request.text, "voice": request.voice or "alloy"}
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.content
        return SynthesisResponse(
            provider_name=self.name,
            mime_type="audio/mpeg",
            audio_bytes=data,
            duration_ms=None,
            metadata={},
        )
