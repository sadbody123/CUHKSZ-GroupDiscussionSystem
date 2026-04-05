"""Rule-based team coordination hints (deterministic)."""

from __future__ import annotations

from typing import Any


def team_memory_summary(
    team_id: str,
    participants: list[dict[str, Any]],
    *,
    user_team_id: str | None,
) -> str:
    """Short line for prompts."""
    members = [p for p in participants if p.get("team_id") == team_id]
    names = [str(p.get("display_name") or p.get("participant_id")) for p in members]
    side = "your side" if team_id == user_team_id else "other side"
    return f"Team {team_id} ({side}): " + ", ".join(names)


def coordination_hint(
    *,
    speaker_team: str | None,
    user_team_id: str | None,
    phase: str,
) -> str:
    if phase == "discussion":
        if speaker_team and user_team_id and speaker_team == user_team_id:
            return "Coordinate with your side: add examples or clarify; avoid repeating the same claim."
        return "Challenge or reframe the other side; ask clarifying questions."
    return "Stay concise and phase-appropriate."
