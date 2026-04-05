"""Vector similarity helpers."""

from __future__ import annotations

import numpy as np


def cosine_similarity_matrix(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """query shape (d,), matrix (n, d) -> scores (n,)"""
    q = query.astype(np.float64)
    m = matrix.astype(np.float64)
    qn = np.linalg.norm(q)
    if qn <= 0:
        return np.zeros((m.shape[0],), dtype=np.float64)
    q = q / qn
    mn = np.linalg.norm(m, axis=1, keepdims=True)
    mn = np.where(mn <= 0, 1.0, mn)
    m = m / mn
    return m @ q
