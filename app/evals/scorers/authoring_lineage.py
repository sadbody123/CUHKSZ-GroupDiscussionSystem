"""Scorer stub for lineage_case."""

from __future__ import annotations

from typing import Any


def score(result: dict[str, Any], expected: dict[str, Any]) -> float:
    return 1.0 if result.get("passed") else 0.0
