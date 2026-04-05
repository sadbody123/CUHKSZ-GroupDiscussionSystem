"""Base embedder."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.indexing.schemas.embedding import EmbeddingRequest, EmbeddingResponse


class BaseEmbedder(ABC):
    name: str = "base"

    @abstractmethod
    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
