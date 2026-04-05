"""Scoring hook for handover_kit_case."""

from __future__ import annotations

from typing import Any


def score_handover_kit(details: dict[str, Any]) -> float:
    return 1.0 if details.get("required_files_present") else 0.0
