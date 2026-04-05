"""Hash embedder determinism."""

from __future__ import annotations

from app.indexing.embedders.hash_embedder import HashEmbedder
from app.indexing.schemas.embedding import EmbeddingRequest


def test_hash_embedder_stable() -> None:
    h = HashEmbedder(dimension=64)
    r1 = h.embed_texts(EmbeddingRequest(texts=["hello world"], embedder_name="hash"))
    r2 = h.embed_texts(EmbeddingRequest(texts=["hello world"], embedder_name="hash"))
    assert r1.dimension == 64
    assert r1.vectors == r2.vectors
