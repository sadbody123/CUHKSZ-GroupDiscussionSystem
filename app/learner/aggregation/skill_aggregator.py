"""Map one session + optional speech report to heuristic skill scores (0–100)."""

from __future__ import annotations

from typing import Any

from app.learner.constants import (
    ALL_SKILL_IDS,
    SPEECH_PROXY_DISCLAIMER_DEFAULT,
    SPEECH_PROXY_SKILL_IDS,
    TEXT_SKILL_IDS,
)
from app.learner.schemas.skill import SkillScore
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.schemas.session import SessionContext


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _signal_ids(signals: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for s in signals:
        i = s.get("id")
        if i:
            out.add(str(i))
    return out


def compute_session_skill_scores(
    ctx: SessionContext,
    *,
    speech_report: dict[str, Any] | None = None,
) -> tuple[dict[str, float | None], dict[str, Any]]:
    """Return (skill_id -> score or None for unknown speech proxies), metrics bundle."""
    metrics: dict[str, Any] = {}
    text_scores: dict[str, float] = {k: 55.0 for k in TEXT_SKILL_IDS}
    metrics, sigs = analyze_transcript_turns(ctx.turns)
    ids = _signal_ids(sigs)

    if "few_examples_risk" in ids:
        text_scores["example_usage"] -= 18.0
    if "example_language" in ids:
        text_scores["example_usage"] += 12.0
    if "discussion_language" in ids:
        text_scores["discussion_language"] += 10.0
    if "support_teammate_language" in ids:
        text_scores["teammate_support"] += 10.0
    if "response_linkage" in ids:
        text_scores["interaction"] += 8.0
        text_scores["rebuttal_clarity"] += 8.0
    if "low_interaction_risk" in ids:
        text_scores["interaction"] -= 22.0
    if "long_turn_risk" in ids:
        text_scores["turn_concision"] -= 15.0

    ut = int(metrics.get("user_turns") or 0)
    tt = max(1, int(metrics.get("total_turns") or 1))
    ratio = ut / tt
    text_scores["content_support"] += (ratio - 0.35) * 40.0
    text_scores["topic_focus"] += 10.0 if ratio >= 0.25 else -8.0

    for k in TEXT_SKILL_IDS:
        text_scores[k] = round(_clamp(text_scores[k]), 2)

    out: dict[str, float | None] = {k: text_scores[k] for k in TEXT_SKILL_IDS}
    for k in SPEECH_PROXY_SKILL_IDS:
        out[k] = None

    sp: dict[str, float] = {}
    if speech_report and (speech_report.get("aggregate_metrics") or {}).get("turns_analyzed"):
        agg = speech_report.get("aggregate_metrics") or {}
        wpm = agg.get("mean_words_per_minute")
        if wpm is not None:
            w = float(wpm)
            # Target band ~100–170 WPM as "comfortable" for discussion practice (heuristic)
            sp["fluency_proxy"] = _clamp(45.0 + (w - 90.0) * 0.35)
            sp["pace_control_proxy"] = _clamp(55.0 - abs(w - 135.0) * 0.25 + 20.0)
        pr = agg.get("mean_pause_ratio")
        if pr is not None:
            p = float(pr)
            sp["pause_management_proxy"] = _clamp(95.0 - p * 400.0)
        fillers = int(agg.get("total_filler_count") or 0)
        sp["delivery_proxy"] = _clamp(88.0 - min(40.0, fillers * 3.0))
        risks = speech_report.get("risks") or []
        strengths = speech_report.get("strengths") or []
        base_conf = 62.0 + min(20.0, len(strengths) * 3.0) - min(25.0, len(risks) * 2.5)
        sp["confidence_proxy"] = _clamp(base_conf)
        for k, v in sp.items():
            out[k] = round(v, 2)
    else:
        for k in SPEECH_PROXY_SKILL_IDS:
            out[k] = None

    bundle = {
        "transcript_metrics": metrics,
        "signal_ids": sorted(ids),
        "has_speech_aggregate": bool(
            speech_report and (speech_report.get("aggregate_metrics") or {}).get("turns_analyzed")
        ),
        "topic_id": ctx.topic_id,
        "runtime_profile_id": ctx.runtime_profile_id,
    }
    return out, bundle


def skill_scores_to_models(
    scores: dict[str, float | None],
    *,
    evidence_count: int = 1,
) -> list[SkillScore]:
    """Flatten session-level scores into SkillScore rows (no trend yet)."""
    from app.learner.constants import SKILL_DISPLAY_NAMES

    out: list[SkillScore] = []
    for sid in ALL_SKILL_IDS:
        val = scores.get(sid)
        disc = None
        if sid in SPEECH_PROXY_SKILL_IDS and val is not None:
            disc = SPEECH_PROXY_DISCLAIMER_DEFAULT
        out.append(
            SkillScore(
                skill_id=sid,
                skill_name=SKILL_DISPLAY_NAMES.get(sid, sid),
                current_score=val,
                recent_score=val,
                baseline_score=val,
                trend="unknown" if val is None else "stable",
                evidence_count=evidence_count if val is not None else 0,
                proxy_disclaimer=disc if sid in SPEECH_PROXY_SKILL_IDS else None,
            )
        )
    return out
