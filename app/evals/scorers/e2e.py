"""End-to-end scoring hooks (see runners/e2e_runner.py)."""

from __future__ import annotations

from typing import Any


def score_e2e(details: dict[str, Any]) -> float:
    scenarios_passed = details.get("scenarios_passed", 0)
    total_scenarios = details.get("total_scenarios", 1)
    return scenarios_passed / total_scenarios
