"""Transcription orchestration (provider only; persistence in AudioService)."""

from __future__ import annotations

from app.audio.providers.asr_base import BaseASRProvider
from app.audio.schemas.asr import TranscriptionRequest, TranscriptionResponse


def transcribe(request: TranscriptionRequest, provider: BaseASRProvider) -> TranscriptionResponse:
    return provider.transcribe(request)
