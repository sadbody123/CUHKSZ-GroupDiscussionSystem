"""Audio schemas."""

from __future__ import annotations

from app.audio.schemas.audio import AudioAssetRecord
from app.audio.schemas.asr import TranscriptionRequest, TranscriptionResponse
from app.audio.schemas.tts import SynthesisRequest, SynthesisResponse

__all__ = [
    "AudioAssetRecord",
    "TranscriptionRequest",
    "TranscriptionResponse",
    "SynthesisRequest",
    "SynthesisResponse",
]
