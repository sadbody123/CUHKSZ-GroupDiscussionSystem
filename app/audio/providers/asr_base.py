"""ASR provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.audio.schemas.asr import TranscriptionRequest, TranscriptionResponse


class BaseASRProvider(ABC):
    name: str = "asr"

    @abstractmethod
    def transcribe(self, request: TranscriptionRequest) -> TranscriptionResponse:
        raise NotImplementedError
