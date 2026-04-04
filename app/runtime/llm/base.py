"""Abstract LLM provider."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.runtime.schemas.llm import GenerationRequest, GenerationResponse


class BaseLLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError
