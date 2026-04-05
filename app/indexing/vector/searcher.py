"""Vector similarity search."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from app.indexing.embedders.base import BaseEmbedder
from app.indexing.schemas.embedding import EmbeddingRequest
from app.indexing.vector.similarity import cosine_similarity_matrix
from app.indexing.vector.store import load_vector_store


class VectorSearcher:
    def __init__(self, npy_path: Path, meta_path: Path, docs_by_id: dict[str, dict[str, Any]]) -> None:
        self._mat, self._meta = load_vector_store(npy_path, meta_path)
        self._ids: list[str] = list(self._meta.get("item_ids") or [])
        self._docs_by_id = docs_by_id

    def search(self, embedder: BaseEmbedder, query_text: str, *, top_k: int) -> list[tuple[str, float, dict[str, Any]]]:
        q = embedder.embed_texts(EmbeddingRequest(texts=[query_text], embedder_name=embedder.name))
        qv = np.array(q.vectors[0], dtype=np.float64)
        scores = cosine_similarity_matrix(qv, self._mat.astype(np.float64))
        order = np.argsort(-scores)
        out: list[tuple[str, float, dict[str, Any]]] = []
        for i in order[:top_k]:
            idx = int(i)
            eid = self._ids[idx] if idx < len(self._ids) else ""
            sc = float(scores[idx])
            out.append((eid, sc, self._docs_by_id.get(eid, {})))
        return out
