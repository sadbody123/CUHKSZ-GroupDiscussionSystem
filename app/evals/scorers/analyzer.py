"""Analyzer scoring hooks (see runners/analyzer_runner.py)."""

from __future__ import annotations

from typing import Any


def score_analyzer(details: dict[str, Any]) -> float:
    analysis_depth = details.get("analysis_depth", 0.5)
    evidence_usage_score = details.get("evidence_usage_score", 0.5)
    citation_quality = details.get("citation_quality", 0.5)
    return (analysis_depth + evidence_usage_score + citation_quality) / 3.0
