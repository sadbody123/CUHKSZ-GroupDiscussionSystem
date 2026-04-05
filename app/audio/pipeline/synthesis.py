"""Synthesis orchestration."""

from __future__ import annotations

from app.audio.providers.tts_base import BaseTTSProvider
from app.audio.schemas.tts import SynthesisRequest, SynthesisResponse


def synthesize(request: SynthesisRequest, provider: BaseTTSProvider) -> SynthesisResponse:
    return provider.synthesize(request)
