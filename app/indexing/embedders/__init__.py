"""Embedder registry."""

from __future__ import annotations

from app.indexing.embedders.base import BaseEmbedder
from app.indexing.embedders.hash_embedder import HashEmbedder


def get_embedder(name: str, *, dimension: int = 128, model_name: str | None = None) -> BaseEmbedder:
    n = (name or "hash").lower().strip()
    if n in ("hash", "deterministic", "local"):
        return HashEmbedder(dimension=dimension)
    if n in ("sentence_transformers", "st", "sentence-transformers"):
        from app.indexing.embedders.sentence_transformers_embedder import SentenceTransformersEmbedder

        return SentenceTransformersEmbedder(model_name=model_name or "all-MiniLM-L6-v2")
    if n in ("openai", "openai_compatible", "openai-compatible"):
        from app.indexing.embedders.openai_embedding import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider(model=model_name)
    return HashEmbedder(dimension=dimension)
