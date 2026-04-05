"""Longitudinal trends from ordered progress points."""

from __future__ import annotations

from typing import Any

from app.learner.constants import ALL_SKILL_IDS, SPEECH_PROXY_SKILL_IDS, SKILL_DISPLAY_NAMES
from app.learner.schemas.skill import SkillScore


def _mean(vals: list[float]) -> float | None:
    if not vals:
        return None
    return round(sum(vals) / len(vals), 3)


def build_skill_scores_from_timeline(
    points: list[dict[str, Any]],
    *,
    recent_window: int = 3,
    baseline_window: int = 3,
) -> list[SkillScore]:
    """Build SkillScore list with current / recent / baseline / trend."""
    if not points:
        return []

    ordered = sorted(points, key=lambda p: str(p.get("created_at") or ""))
    last = ordered[-1]
    last_skills: dict[str, float | None] = {}
    raw_last = last.get("skill_scores") or {}
    for k, v in raw_last.items():
        if v is None:
            last_skills[k] = None
        else:
            try:
                last_skills[k] = float(v)
            except (TypeError, ValueError):
                last_skills[k] = None

    def collect(skill: str, which: str) -> list[float]:
        seq = ordered if which == "all" else (ordered[-recent_window:] if which == "recent" else ordered[:baseline_window])
        out: list[float] = []
        for pt in seq:
            ss = pt.get("skill_scores") or {}
            val = ss.get(skill)
            if val is None:
                continue
            try:
                out.append(float(val))
            except (TypeError, ValueError):
                continue
        return out

    out: list[SkillScore] = []
    for sid in ALL_SKILL_IDS:
        cur = last_skills.get(sid)
        recent_m = _mean(collect(sid, "recent"))
        base_m = _mean(collect(sid, "baseline"))
        trend = "unknown"
        if cur is None and sid in SPEECH_PROXY_SKILL_IDS:
            trend = "unknown"
        elif recent_m is None or base_m is None:
            trend = "unknown"
        else:
            delta = recent_m - base_m
            if delta > 3.0:
                trend = "improving"
            elif delta < -3.0:
                trend = "declining"
            else:
                trend = "stable"
        ev = sum(1 for pt in ordered if (pt.get("skill_scores") or {}).get(sid) is not None)
        disc = None
        if sid in SPEECH_PROXY_SKILL_IDS and cur is not None:
            from app.learner.constants import SPEECH_PROXY_DISCLAIMER_DEFAULT

            disc = SPEECH_PROXY_DISCLAIMER_DEFAULT
        out.append(
            SkillScore(
                skill_id=sid,
                skill_name=SKILL_DISPLAY_NAMES.get(sid, sid),
                current_score=cur,
                recent_score=recent_m,
                baseline_score=base_m,
                trend=trend,
                evidence_count=int(ev),
                proxy_disclaimer=disc,
            )
        )
    return out


def rank_weak_strong(
    skills: list[SkillScore],
    *,
    top_n: int = 4,
) -> tuple[list[str], list[str], list[str]]:
    """Return (weak_ids, strong_ids, focus_ids) using scores where available."""
    rated: list[tuple[str, float]] = []
    for s in skills:
        if s.current_score is None:
            continue
        rated.append((s.skill_id, float(s.current_score)))
    rated.sort(key=lambda x: x[1])
    weak = [x[0] for x in rated[:top_n]]
    strong = [x[0] for x in sorted(rated, key=lambda x: x[1], reverse=True)[:top_n]]
    focus = weak[:3] if weak else [x[0] for x in rated[:2]]
    return weak, strong, focus
