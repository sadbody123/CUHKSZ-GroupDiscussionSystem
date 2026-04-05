"""Combine lexical and vector hit lists."""

from __future__ import annotations

from typing import Any


def _norm_scores(pairs: list[tuple[str, float]]) -> dict[str, float]:
    if not pairs:
        return {}
    scores = [p[1] for p in pairs]
    lo, hi = min(scores), max(scores)
    out: dict[str, float] = {}
    if hi <= lo:
        for i, p in enumerate(pairs):
            out[p[0]] = 1.0 - i * 1e-6
        return out
    for pid, s in pairs:
        out[pid] = (s - lo) / (hi - lo)
    return out


def merge_hybrid(
    lexical: list[tuple[str, float, dict[str, Any]]],
    vector: list[tuple[str, float, dict[str, Any]]],
    *,
    lexical_weight: float,
    vector_weight: float,
    top_k: int,
) -> list[tuple[str, float, dict[str, Any]]]:
    lx = _norm_scores([(a, b) for a, b, _ in lexical])
    vx = _norm_scores([(a, b) for a, b, _ in vector])
    meta: dict[str, dict[str, Any]] = {}
    for pid, _s, m in lexical + vector:
        meta.setdefault(pid, {}).update(m)
    ids = set(lx.keys()) | set(vx.keys())
    fused: list[tuple[str, float, dict[str, Any]]] = []
    for pid in ids:
        s = lexical_weight * lx.get(pid, 0.0) + vector_weight * vx.get(pid, 0.0)
        fused.append((pid, s, meta.get(pid, {})))
    fused.sort(key=lambda x: x[1], reverse=True)
    return fused[:top_k]
