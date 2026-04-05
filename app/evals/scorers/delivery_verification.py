"""Scoring hook for delivery_verification_case."""

from __future__ import annotations

from typing import Any


def score_delivery_verification(details: dict[str, Any]) -> float:
    st = details.get("overall_status")
    return 1.0 if st in ("ok", "warning") else 0.5 if st == "blocked" else 0.0
