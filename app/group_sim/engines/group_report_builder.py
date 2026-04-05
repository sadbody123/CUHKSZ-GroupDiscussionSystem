"""Build GroupBalanceReport from session + stats."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.group_sim.constants import GROUP_PRACTICE_NOTE
from app.group_sim.engines.speaking_balance import balance_flags, compute_participant_stats, compute_team_stats
from app.group_sim.schemas.report import GroupBalanceReport
from app.runtime.schemas.session import SessionContext


def build_group_balance_report(ctx: SessionContext) -> GroupBalanceReport:
    participants = list(ctx.participants or [])
    teams = list(ctx.teams or [])
    ps = compute_participant_stats(ctx.turns, participants=participants)
    ts = compute_team_stats(ctx.turns, teams=teams, participants=participants)
    flags = balance_flags(
        ps,
        ts,
        user_participant_id=ctx.user_participant_id,
        participants=participants,
    )
    strengths: list[str] = []
    risks: list[str] = []
    recs: list[str] = []
    if len({f.get("type") for f in flags}) == 0:
        strengths.append("Participation spread looks reasonable for a short practice session.")
    for f in flags:
        if f.get("type") == "dominant_speaker":
            risks.append(f"Participant {f.get('participant_id')} may be dominating airtime.")
            recs.append("Invite other seats to respond or ask a clarifying question.")
        if f.get("type") == "low_user_participation":
            risks.append("User seat has relatively few turns — practice adding concise interjections.")
            recs.append("Aim for at least one contribution per discussion round.")
        if f.get("type") == "team_turn_imbalance":
            risks.append("Teams may not be balanced in discussion turns (practice metric only).")
    rid = str(uuid.uuid4())
    return GroupBalanceReport(
        report_id=rid,
        session_id=ctx.session_id,
        roster_template_id=ctx.roster_template_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        participant_stats=ps,
        team_stats=ts,
        balance_flags=flags,
        strengths=strengths,
        risks=risks,
        recommendations=recs,
        metadata={"practice_note": GROUP_PRACTICE_NOTE, "not_exam_score": True},
    )
