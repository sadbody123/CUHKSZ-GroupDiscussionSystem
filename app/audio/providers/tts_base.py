"""TTS provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.audio.schemas.tts import SynthesisRequest, SynthesisResponse


class BaseTTSProvider(ABC):
    name: str = "tts"

    @abstractmethod
    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        raise NotImplementedError
