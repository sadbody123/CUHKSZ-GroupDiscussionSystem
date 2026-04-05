"""Scoring hook for demo_kit_case."""

from __future__ import annotations

from typing import Any


def score_demo_kit(details: dict[str, Any]) -> float:
    return 1.0 if details.get("demo_kit_manifest") else 0.0
