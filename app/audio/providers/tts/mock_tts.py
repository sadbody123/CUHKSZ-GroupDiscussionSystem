"""Deterministic offline TTS (WAV bytes)."""

from __future__ import annotations

from app.audio.pipeline.wave_utils import wav_bytes_from_seed
from app.audio.providers.tts_base import BaseTTSProvider
from app.audio.schemas.tts import SynthesisRequest, SynthesisResponse


class MockTTSProvider(BaseTTSProvider):
    name = "mock_tts"

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        seed = f"{request.text}|{request.role or ''}|{request.voice or ''}"
        b = wav_bytes_from_seed(seed)
        return SynthesisResponse(
            provider_name=self.name,
            mime_type="audio/wav",
            audio_bytes=b,
            duration_ms=400,
            raw={"mock": True},
            metadata=dict(request.metadata),
        )
