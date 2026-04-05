"""Resolve ASR/TTS providers by name."""

from __future__ import annotations

from pathlib import Path

from app.audio.providers.asr.mock_asr import MockASRProvider
from app.audio.providers.asr_base import BaseASRProvider
from app.audio.providers.tts.mock_tts import MockTTSProvider
from app.audio.providers.tts_base import BaseTTSProvider
from app.ops.settings import UnifiedSettings, get_ops_settings


def _default_manifest_path(settings: UnifiedSettings) -> Path:
    if settings.mock_asr_manifest_path:
        return Path(settings.mock_asr_manifest_path)
    bundled = Path(__file__).resolve().parents[1] / "data" / "mock_asr_manifest.json"
    return bundled


def get_asr_provider(name: str | None, settings: UnifiedSettings | None = None) -> BaseASRProvider:
    s = settings or get_ops_settings()
    n = (name or s.default_asr_provider or "mock_asr").lower().strip()
    if n in ("mock_asr", "mock", "offline"):
        return MockASRProvider(manifest_path=_default_manifest_path(s))
    if n in ("openai_whisper", "openai-whisper", "whisper"):
        from app.audio.providers.asr.openai_whisper_compatible import OpenAIWhisperCompatibleProvider

        return OpenAIWhisperCompatibleProvider(model=s.openai_transcribe_model)
    if n == "local_whisper_stub":
        from app.audio.providers.asr.local_whisper_stub import LocalWhisperStubProvider

        return LocalWhisperStubProvider(manifest_path=_default_manifest_path(s))
    return MockASRProvider(manifest_path=_default_manifest_path(s))


def get_tts_provider(name: str | None, settings: UnifiedSettings | None = None) -> BaseTTSProvider:
    s = settings or get_ops_settings()
    n = (name or s.default_tts_provider or "mock_tts").lower().strip()
    if n in ("mock_tts", "mock", "offline"):
        return MockTTSProvider()
    if n in ("openai_tts", "openai-tts"):
        from app.audio.providers.tts.openai_tts_compatible import OpenAITTSCompatibleProvider

        return OpenAITTSCompatibleProvider(model=s.openai_tts_model)
    if n == "local_tts_stub":
        from app.audio.providers.tts.local_tts_stub import LocalTTSStubProvider

        return LocalTTSStubProvider()
    return MockTTSProvider()
