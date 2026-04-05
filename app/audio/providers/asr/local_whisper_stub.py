"""Placeholder for local Whisper (not wired by default)."""

from __future__ import annotations

from app.audio.providers.asr.mock_asr import MockASRProvider


class LocalWhisperStubProvider(MockASRProvider):
    """Delegates to mock until a local engine is integrated."""

    name = "local_whisper_stub"
