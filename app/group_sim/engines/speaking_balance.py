"""Aggregate speaking statistics from transcript."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.group_sim.schemas.balance import ParticipantTurnStats, TeamTurnStats
from app.runtime.schemas.transcript import TranscriptTurn


def compute_participant_stats(
    turns: list[TranscriptTurn],
    *,
    participants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_pid: dict[str, ParticipantTurnStats] = {}
    for p in participants:
        pid = str(p.get("participant_id") or "")
        by_pid[pid] = ParticipantTurnStats(participant_id=pid)
    for t in turns:
        pid = None
        if getattr(t, "participant_id", None):
            pid = str(t.participant_id)
        if not pid:
            continue
        st = by_pid.setdefault(pid, ParticipantTurnStats(participant_id=pid))
        st.turn_count += 1
        st.total_chars += len(t.text or "")
        ph = (t.metadata or {}).get("phase") or "discussion"
        st.phase_counts[ph] = st.phase_counts.get(ph, 0) + 1
    out: list[dict[str, Any]] = []
    for st in by_pid.values():
        if st.turn_count:
            st.avg_chars_per_turn = round(st.total_chars / st.turn_count, 2)
        out.append(st.model_dump())
    return sorted(out, key=lambda x: x["participant_id"])


def compute_team_stats(
    turns: list[TranscriptTurn],
    *,
    teams: list[dict[str, Any]],
    participants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    team_pids: dict[str, set[str]] = {str(t["team_id"]): set(t.get("participant_ids") or []) for t in teams}
    stats: dict[str, TeamTurnStats] = {tid: TeamTurnStats(team_id=tid) for tid in team_pids}
    pid_to_team = {str(p["participant_id"]): str(p.get("team_id") or "") for p in participants}
    for t in turns:
        pid = str(getattr(t, "participant_id", "") or "")
        tid = str(getattr(t, "team_id", "") or "") or pid_to_team.get(pid, "")
        if not tid or tid not in stats:
            continue
        st = stats[tid]
        st.turn_count += 1
        st.total_chars += len(t.text or "")
        ph = (t.metadata or {}).get("phase") or ""
        if ph == "intro":
            st.intro_done = True
        if ph == "summary":
            st.summary_done = True
        if ph == "discussion":
            st.discussion_turns += 1
    return [s.model_dump() for s in stats.values()]


def balance_flags(
    participant_stats: list[dict[str, Any]],
    team_stats: list[dict[str, Any]],
    *,
    user_participant_id: str | None,
    participants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    if not participant_stats:
        return flags
    total_turns = sum(int(p.get("turn_count") or 0) for p in participant_stats)
    if total_turns == 0:
        return flags
    for p in participant_stats:
        pid = str(p.get("participant_id") or "")
        share = int(p.get("turn_count") or 0) / total_turns
        if share > 0.45:
            flags.append({"type": "dominant_speaker", "participant_id": pid, "share": round(share, 3)})
    if user_participant_id:
        up = next((x for x in participant_stats if x.get("participant_id") == user_participant_id), None)
        if up and int(up.get("turn_count") or 0) / total_turns < 0.12:
            flags.append({"type": "low_user_participation", "participant_id": user_participant_id})
    if len(team_stats) >= 2:
        tcs = [int(t.get("turn_count") or 0) for t in team_stats]
        if max(tcs) > 0 and min(tcs) / max(tcs) < 0.35:
            flags.append({"type": "team_turn_imbalance", "detail": tcs})
    return flags
