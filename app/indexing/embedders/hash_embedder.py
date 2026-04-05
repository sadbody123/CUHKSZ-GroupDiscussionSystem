"""Deterministic local embedder (no network, no model files)."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Iterable

import numpy as np

from app.indexing.embedders.base import BaseEmbedder
from app.indexing.schemas.embedding import EmbeddingRequest, EmbeddingResponse

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> Iterable[str]:
    yield from _TOKEN.findall(text.lower())


class HashEmbedder(BaseEmbedder):
    """Feature hashing into a fixed dense vector, L2-normalized."""

    name = "hash"

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = int(dimension)

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResponse:
        vecs: list[list[float]] = []
        for t in request.texts:
            v = np.zeros(self.dimension, dtype=np.float64)
            for tok in _tokens(t):
                h = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
                idx = int.from_bytes(h[:4], "little") % self.dimension
                sign = -1.0 if (h[4] & 1) else 1.0
                v[idx] += sign * (1.0 + math.log1p(len(tok)))
            n = float(np.linalg.norm(v))
            if n > 0:
                v = v / n
            vecs.append(v.tolist())
        return EmbeddingResponse(
            embedder_name=self.name,
            model_name=request.model_name,
            vectors=vecs,
            dimension=self.dimension,
            metadata={"hash": "blake2b-token"},
        )
