"""Metadata-based score boosts."""

from __future__ import annotations

from typing import Any


def boost_evidence_score(
    score: float,
    meta: dict[str, Any],
    *,
    quality_boost: float,
    credibility_boost: float,
) -> float:
    q = float(meta.get("quality_score") or 0.0)
    c = float(meta.get("credibility_score") or 0.0)
    return score * (1.0 + quality_boost * q) * (1.0 + credibility_boost * c)
