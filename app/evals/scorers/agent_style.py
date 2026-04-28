"""Agent style scoring hooks (see runners/agent_runner.py)."""

from __future__ import annotations

from typing import Any


def score_agent_style(details: dict[str, Any]) -> float:
    role_adherence_score = details.get("role_adherence_score", 0.5)
    tone_match_score = details.get("tone_match_score", 0.5)
    return (role_adherence_score + tone_match_score) / 2.0
