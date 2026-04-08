"""Embedding provider abstraction."""

from __future__ import annotations

from abc import abstractmethod

from app.agent_runtime_v2.providers.base import ProviderBase
from app.agent_runtime_v2.providers.models import EmbeddingRequest, EmbeddingResponse


class EmbeddingProvider(ProviderBase):
    @abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
