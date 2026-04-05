"""Build ReviewPack from session + optional artifacts."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.audio.analysis.pipeline.report_store import SpeechReportStore
from app.group_sim.store.group_report_store import GroupReportStore
from app.modes.store.mode_report_store import ModeReportStore
from app.review.constants import PACK_PENDING, PROXY_DISCLAIMER_NOTE
from app.review.engines.rubric_mapper import build_rubric_dimensions_for_snapshot
from app.review.schemas.pack import ReviewPack
from app.runtime.schemas.session import SessionContext


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summarize_coach(cr: dict[str, Any] | None) -> dict[str, Any]:
    if not cr:
        return {}
    return {
        "main_strengths": (cr.get("strengths") or [])[:8],
        "main_risks": (cr.get("risks") or [])[:8],
        "speech_strengths": (cr.get("speech_strengths") or [])[:6],
        "speech_risks": (cr.get("speech_risks") or [])[:6],
        "proxy_limitations": cr.get("proxy_limitations") or [],
    }


def build_review_pack(
    ctx: SessionContext,
    *,
    speech_report_dir: Path,
    mode_reports_dir: Path,
    group_reports_dir: Path,
    learner_summary: dict[str, Any] | None = None,
) -> ReviewPack:
    """Aggregate session transcript refs and artifact summaries (best-effort)."""
    session_id = ctx.session_id
    snap = Path(ctx.snapshot_dir) if ctx.snapshot_dir else None

    included: dict[str, Any] = {
        "session": {
            "runtime_profile_id": ctx.runtime_profile_id,
            "mode_id": ctx.mode_id,
            "preset_id": ctx.preset_id,
            "assessment_template_id": ctx.assessment_template_id,
            "roster_template_id": ctx.roster_template_id,
            "phase": ctx.phase,
            "turn_count": len(ctx.turns),
            "participants": len(ctx.participants),
        },
        "feedback_packet": (ctx.coach_report or {}).get("feedback_packet"),
        "coach_report": ctx.coach_report,
        "transcript_turns": [t.model_dump() for t in ctx.turns[-50:]],
    }

    proxy_notes: list[str] = [PROXY_DISCLAIMER_NOTE]
    if ctx.coach_report and (ctx.coach_report.get("proxy_limitations") or []):
        proxy_notes.extend(str(x) for x in ctx.coach_report["proxy_limitations"])

    # Speech session report (reference only, no audio bytes)
    speech_ref = f"speech_reports/{session_id}/session_report.json"
    try:
        sp = SpeechReportStore(speech_report_dir).load_session_report(session_id)
        if sp:
            included["session_speech_report"] = sp.model_dump() if hasattr(sp, "model_dump") else sp.dict()  # type: ignore[union-attr]
    except Exception:
        included["session_speech_report"] = None

    # Mode report
    try:
        mr = ModeReportStore(mode_reports_dir).load_by_session(session_id)
        included["mode_report"] = mr.model_dump() if mr else None
    except Exception:
        included["mode_report"] = None

    # Group balance
    try:
        gr = GroupReportStore(group_reports_dir).load_by_session(session_id)
        included["group_balance_report"] = gr.model_dump() if gr else None
    except Exception:
        included["group_balance_report"] = None

    if learner_summary:
        included["learner_summary"] = learner_summary

    rubric_dims = [d.model_dump() for d in build_rubric_dimensions_for_snapshot(snap)]

    ai_summary = {
        "main_strengths": _summarize_coach(ctx.coach_report).get("main_strengths", []),
        "main_risks": _summarize_coach(ctx.coach_report).get("main_risks", []),
        "flags": [],
        "relevant_metrics": {
            "turn_count": len(ctx.turns),
            "has_speech_report": bool(included.get("session_speech_report")),
            "has_mode_report": bool(included.get("mode_report")),
            "has_group_report": bool(included.get("group_balance_report")),
        },
        "rubric_dimensions": rubric_dims,
    }

    pack = ReviewPack(
        review_pack_id=str(uuid.uuid4()),
        session_id=session_id,
        learner_id=ctx.learner_id,
        topic_id=ctx.topic_id,
        mode_id=ctx.mode_id,
        roster_template_id=ctx.roster_template_id,
        created_at=_iso(),
        status=PACK_PENDING,
        included_artifacts=included,
        ai_summary=ai_summary,
        transcript_ref=speech_ref,
        proxy_limitations=proxy_notes,
        metadata={"builder_version": "1"},
    )
    return pack
