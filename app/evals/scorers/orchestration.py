"""Orchestration scoring hooks (see runners/state_machine_runner.py)."""

from __future__ import annotations

from typing import Any


def score_orchestration(details: dict[str, Any]) -> float:
    correct_transitions = details.get("correct_transitions", 0)
    total_transitions = details.get("total_transitions", 1)
    return correct_transitions / total_transitions
