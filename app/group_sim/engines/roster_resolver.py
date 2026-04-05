"""Build concrete roster for a session from template + user seat."""

from __future__ import annotations

from typing import Any

from app.group_sim.schemas.roster import RosterTemplate


def build_participants_and_teams(
    template: RosterTemplate,
    *,
    user_participant_id: str,
    participant_name_overrides: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return serialized participants and teams with controller_type / relation_to_user resolved."""
    overrides = participant_name_overrides or {}
    user_team: str | None = None
    for p in template.participants:
        if p.get("participant_id") == user_participant_id:
            user_team = str(p.get("team_id") or "")
            break
    if user_team is None:
        user_team = str(template.participants[0].get("team_id") or "")

    participants: list[dict[str, Any]] = []
    for raw in template.participants:
        d = dict(raw)
        pid = str(d.get("participant_id") or "")
        if pid in overrides:
            d["display_name"] = overrides[pid]
        if pid == user_participant_id:
            d["controller_type"] = "user"
            d["relation_to_user"] = "self"
        else:
            d["controller_type"] = str(d.get("controller_type") or "agent")
            if d["controller_type"] != "user":
                d["controller_type"] = "agent"
            ut = str(d.get("team_id") or "")
            d["relation_to_user"] = "ally" if ut == user_team else "opponent"
        participants.append(d)

    teams = [dict(t) for t in template.teams]
    return participants, teams


def default_seat_policies(participants: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in participants:
        pid = str(p.get("participant_id") or "")
        rel = str(p.get("relation_to_user") or "")
        style = "balanced"
        if rel == "opponent":
            style = "aggressive"
        elif rel == "ally":
            style = "conservative"
        out[pid] = {
            "participant_id": pid,
            "interruption_style": style,
            "target_turn_share": 1.0 / max(1, len(participants)),
            "max_consecutive_turns": 2,
        }
    return out
