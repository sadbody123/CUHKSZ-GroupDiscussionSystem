"""Speech providers."""

from __future__ import annotations

from app.audio.providers.manager import get_asr_provider, get_tts_provider

__all__ = ["get_asr_provider", "get_tts_provider"]
