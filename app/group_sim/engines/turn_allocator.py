"""Seat-aware next speaker selection (single user + AI agents)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.group_sim.engines.intro_summary_planner import intro_order, summary_order
from app.group_sim.engines.participant_memory import get_participant_slice
from app.runtime.enums import RoleType, SessionPhase
from app.runtime.schemas.session import SessionContext


@dataclass
class NextSpeakerPlan:
    next_role: str
    participant_id: str
    team_id: str | None
    display_name: str
    seat_label: str
    relation_to_user: str
    turn_role_type: str
    allocation_reason: str
    candidate_participant_ids: list[str]


def _relation_to_runtime_role(relation: str) -> str:
    r = (relation or "").lower()
    if r == "self":
        return RoleType.USER.value
    if r == "ally":
        return RoleType.ALLY.value
    if r == "opponent":
        return RoleType.OPPONENT.value
    if r == "neutral":
        return RoleType.MODERATOR.value
    return RoleType.ALLY.value


def _turn_role_type(relation: str, controller: str) -> str:
    if (controller or "").lower() == "system":
        return "moderator"
    if (relation or "").lower() == "self":
        return "user"
    if (relation or "").lower() == "ally":
        return "ally_agent"
    if (relation or "").lower() == "opponent":
        return "opponent_agent"
    return "agent"


def _participant_by_id(participants: list[dict[str, Any]], pid: str) -> dict[str, Any] | None:
    for p in participants:
        if str(p.get("participant_id")) == pid:
            return p
    return None


def allocate_next_speaker(ctx: SessionContext, last_role: str | None) -> NextSpeakerPlan | None:
    """If session has roster, return seat plan; otherwise caller uses legacy role machine."""
    if not ctx.participants:
        return None
    participants = list(ctx.participants)
    phase = ctx.phase or SessionPhase.DISCUSSION.value
    last_pid = None
    if ctx.turns:
        last = ctx.turns[-1]
        last_pid = getattr(last, "participant_id", None) or (last.metadata or {}).get("participant_id")

    if phase == SessionPhase.INTRO.value:
        order = intro_order(participants)
        if not order:
            return None
        if not last_pid or last_pid not in order:
            next_pid = order[0]
        else:
            i = order.index(last_pid)
            next_pid = order[(i + 1) % len(order)]
        p = _participant_by_id(participants, next_pid) or {}
        reason = "intro_round_robin"
        return _plan_from_participant(p, reason, order[:])

    if phase == SessionPhase.SUMMARY.value:
        order = summary_order(participants)
        if not order:
            return None
        if not last_pid or last_pid not in order:
            next_pid = order[0]
        else:
            i = order.index(last_pid)
            next_pid = order[(i + 1) % len(order)]
        p = _participant_by_id(participants, next_pid) or {}
        reason = "summary_round_robin"
        return _plan_from_participant(p, reason, order[:])

    if phase in (SessionPhase.DISCUSSION.value, SessionPhase.PREPARE.value):
        # Round-robin by participant_id order; skip tightening for now
        p_sorted = sorted(participants, key=lambda x: str(x.get("participant_id")))
        ids = [str(p.get("participant_id")) for p in p_sorted]
        if not ids:
            return None
        if not last_pid or last_pid not in ids:
            nxt = p_sorted[0]
        else:
            i = ids.index(last_pid)
            nxt = p_sorted[(i + 1) % len(p_sorted)]
        reason = "discussion_round_robin"
        return _plan_from_participant(nxt, reason, ids)

    if phase == SessionPhase.FEEDBACK.value:
        return NextSpeakerPlan(
            next_role=RoleType.COACH.value,
            participant_id="coach",
            team_id=None,
            display_name="Coach",
            seat_label="COACH",
            relation_to_user="neutral",
            turn_role_type="coach",
            allocation_reason="feedback_phase",
            candidate_participant_ids=["coach"],
        )

    # ended / unknown — fallback
    return None


def _plan_from_participant(p: dict[str, Any], reason: str, cand: list[str]) -> NextSpeakerPlan:
    pid = str(p.get("participant_id") or "unknown")
    rel = str(p.get("relation_to_user") or "neutral")
    ctrl = str(p.get("controller_type") or "agent")
    nr = _relation_to_runtime_role(rel if ctrl != "user" else "self")
    if ctrl == "user":
        nr = RoleType.USER.value
    trt = _turn_role_type(rel, ctrl)
    return NextSpeakerPlan(
        next_role=nr,
        participant_id=pid,
        team_id=str(p.get("team_id") or None) if p.get("team_id") else None,
        display_name=str(p.get("display_name") or pid),
        seat_label=str(p.get("seat_label") or ""),
        relation_to_user=rel,
        turn_role_type=trt,
        allocation_reason=reason,
        candidate_participant_ids=cand,
    )
