"""Compare AI outputs with human review — deterministic heuristics."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.review.constants import (
    AGREEMENT_HIGH,
    AGREEMENT_LOW,
    AGREEMENT_MEDIUM,
    AGREEMENT_UNKNOWN,
)
from app.review.engines.disagreement_analyzer import analyze_strength_risk_overlap, tag_proxy_overreliance
from app.review.schemas.calibration import CalibrationReport, CalibrationResult
from app.review.schemas.report import HumanReview


def _overlap(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def _score_agreement(ai: float | None, human: float | None) -> tuple[float | None, str]:
    if ai is None or human is None:
        return None, AGREEMENT_UNKNOWN
    d = abs(ai - human)
    if d <= 0.25:
        return d, AGREEMENT_HIGH
    if d <= 1.0:
        return d, AGREEMENT_MEDIUM
    return d, AGREEMENT_LOW


def build_calibration_report(
    *,
    review_pack_id: str,
    session_id: str,
    review_id: str | None,
    coach_report: dict[str, Any] | None,
    human: HumanReview,
) -> CalibrationReport:
    results: list[dict] = []
    key_mismatches: list[str] = []
    suggested: list[str] = []

    ai_strengths = list(coach_report.get("strengths") or []) if coach_report else []
    ai_risks = list(coach_report.get("risks") or []) if coach_report else []
    human_notes = [a.get("content", "") for a in human.annotations if isinstance(a, dict)]
    human_notes.extend(human.summary_notes)

    disc = analyze_strength_risk_overlap(ai_strengths, ai_risks, human_notes)
    if disc["ai_missing_risk_in_human_view"]:
        key_mismatches.append("ai_may_understate_risks_relative_to_human")
        suggested.append("Review coach risk list against human annotations")
    if disc["human_added_risk_or_concern"]:
        key_mismatches.append("human_only_findings")
    for tag in tag_proxy_overreliance(coach_report):
        key_mismatches.append(f"proxy_metric_note:{tag}")

    # Rubric alignment (first N dimensions)
    hs_map = {str(x.get("dimension_id")): x for x in human.rubric_scores if isinstance(x, dict)}
    for dim_id, row in hs_map.items():
        hscore = row.get("score")
        # pretend AI implied score from coach (placeholder: None)
        ai_implied = None
        dlt, lvl = _score_agreement(ai_implied, float(hscore) if hscore is not None else None)
        cr = CalibrationResult(
            calibration_id=str(uuid.uuid4()),
            component_type="rubric",
            component_id=dim_id,
            ai_value=ai_implied,
            human_value=hscore,
            delta=dlt,
            agreement_level=lvl,
            notes=["rubric human score recorded; AI rubric score not modeled in runtime"],
        )
        results.append(cr.model_dump())

    s_ai = {str(x).lower() for x in ai_strengths}
    s_h = set()
    for line in human_notes:
        s_h.update(str(line).lower().split())
    ov = _overlap(s_ai, s_h)
    str_lvl = AGREEMENT_HIGH if ov > 0.2 else AGREEMENT_MEDIUM if ov > 0.05 else AGREEMENT_LOW
    results.append(
        CalibrationResult(
            calibration_id=str(uuid.uuid4()),
            component_type="feedback",
            component_id="strengths_language_overlap",
            ai_value=list(ai_strengths[:5]),
            human_value=human_notes[:5],
            delta=1.0 - ov,
            agreement_level=str_lvl,
            notes=["token overlap heuristic between strengths and human notes"],
        ).model_dump()
    )

    # Conflicts: human flag disagreement annotations vs AI risks
    for ann in human.annotations:
        if not isinstance(ann, dict):
            continue
        if ann.get("annotation_type") == "disagreement":
            key_mismatches.append(f"human_disagreement:{ann.get('content', '')[:120]}")

    overall = AGREEMENT_MEDIUM
    if any(r.get("agreement_level") == AGREEMENT_LOW for r in results):
        overall = AGREEMENT_LOW
    if results and all(r.get("agreement_level") == AGREEMENT_HIGH for r in results if r.get("agreement_level")):
        overall = AGREEMENT_HIGH

    return CalibrationReport(
        report_id=str(uuid.uuid4()),
        review_pack_id=review_pack_id,
        session_id=session_id,
        review_id=review_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        overall_agreement=overall,
        results=results,
        key_mismatches=key_mismatches[:50],
        suggested_actions=suggested[:20],
        reviewed_output_refs={},
        metadata={"disagreement_analysis": disc},
    )
