"""Retrieval-related scoring hooks (see runners/retrieval_runner.py)."""

from __future__ import annotations

from typing import Any


def score_retrieval(details: dict[str, Any]) -> float:
    precision = details.get("precision", 0.0)
    recall = details.get("recall", 0.0)
    mrr = details.get("mrr", 0.0)
    return (precision + recall + mrr) / 3.0
