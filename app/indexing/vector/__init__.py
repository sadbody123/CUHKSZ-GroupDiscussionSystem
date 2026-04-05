"""Vector index."""

from __future__ import annotations

from app.indexing.vector.builder import build_vectors_for_docs
from app.indexing.vector.searcher import VectorSearcher

__all__ = ["VectorSearcher", "build_vectors_for_docs"]
