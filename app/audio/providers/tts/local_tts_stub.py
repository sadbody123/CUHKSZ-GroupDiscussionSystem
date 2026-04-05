"""Placeholder local TTS — delegates to mock."""

from __future__ import annotations

from app.audio.providers.tts.mock_tts import MockTTSProvider


class LocalTTSStubProvider(MockTTSProvider):
    name = "local_tts_stub"
