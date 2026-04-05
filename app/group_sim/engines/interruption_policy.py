"""Boost opponent priority after long turns or same-team streaks."""

from __future__ import annotations

from typing import Any


def should_boost_opponent(
    *,
    last_participant_team: str | None,
    next_candidate_team: str | None,
    user_team: str | None,
    last_turn_chars: int,
    same_team_streak: int,
    long_turn_threshold: int = 900,
    max_same_team_streak: int = 2,
) -> bool:
    if last_turn_chars >= long_turn_threshold:
        return True
    if user_team and last_participant_team and next_candidate_team:
        if last_participant_team == next_candidate_team == user_team and same_team_streak >= max_same_team_streak:
            return True
    return False
