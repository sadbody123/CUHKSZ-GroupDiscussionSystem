"""Optional sentence-transformers embedder (soft dependency)."""

from __future__ import annotations

from app.indexing.embedders.base import BaseEmbedder
from app.indexing.schemas.embedding import EmbeddingRequest, EmbeddingResponse


class SentenceTransformersEmbedder(BaseEmbedder):
    name = "sentence_transformers"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer(model_name)
        except Exception as e:
            raise RuntimeError(
                "sentence_transformers is not available or model could not load. "
                "Install `sentence-transformers` or use embedder=hash."
            ) from e

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResponse:
        vecs = self._model.encode(request.texts, normalize_embeddings=True)
        rows = [list(map(float, v.tolist())) for v in vecs]
        dim = len(rows[0]) if rows else 0
        return EmbeddingResponse(
            embedder_name=self.name,
            model_name=self.model_name,
            vectors=rows,
            dimension=dim,
            metadata={},
        )
