"""Build vector embeddings for docs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from app.indexing.embedders.base import BaseEmbedder
from app.indexing.schemas.embedding import EmbeddingRequest
from app.indexing.vector.store import save_vector_store


def build_vectors_for_docs(
    embedder: BaseEmbedder,
    docs: list[dict[str, Any]],
    *,
    npy_path: Path,
    meta_path: Path,
) -> tuple[int, int]:
    texts = [str(d.get("text") or "") for d in docs]
    resp = embedder.embed_texts(EmbeddingRequest(texts=texts, embedder_name=embedder.name))
    mat = np.array(resp.vectors, dtype=np.float32)
    ids = [str(d.get("item_id") or "") for d in docs]
    save_vector_store(npy_path, meta_path, mat, ids)
    return mat.shape[0], mat.shape[1]
