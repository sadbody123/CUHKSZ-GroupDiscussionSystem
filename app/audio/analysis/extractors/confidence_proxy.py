"""ASR confidence or explainable proxy (not pronunciation truth)."""

from __future__ import annotations


def blend_confidence_proxy(
    asr_confidence: float | None,
    *,
    filler_ratio: float,
    pause_ratio: float,
    word_count: int,
) -> float:
    """Return 0..1 heuristic score; lower fillers/pauses and reasonable length => higher."""
    base = 0.65
    if asr_confidence is not None:
        base = 0.5 * float(asr_confidence) + 0.5 * base
    penalty = 0.15 * min(1.0, filler_ratio * 5) + 0.1 * min(1.0, pause_ratio * 2)
    boost = 0.0
    if 5 <= word_count <= 200:
        boost = 0.05
    score = max(0.0, min(1.0, base - penalty + boost))
    return round(score, 4)
