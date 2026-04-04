"""Assemble FeedbackPacket from metrics + pedagogy pointers."""

from __future__ import annotations

from app.runtime.repositories.pedagogy_repo import PedagogyRepository
from app.runtime.schemas.feedback import FeedbackPacket


def build_feedback_packet(
    *,
    session_id: str,
    topic_id: str | None,
    metrics: dict,
    detected_signals: list[dict],
    pedagogy: PedagogyRepository,
) -> FeedbackPacket:
    strengths: list[str] = []
    risks: list[str] = []
    for sig in detected_signals:
        sid = sig.get("id", "")
        if "risk" in sid:
            risks.append(str(sid))
        elif sid in ("discussion_language", "example_language", "response_linkage"):
            strengths.append(str(sid))

    rec_ids: list[str] = []
    if any(s.get("id") == "low_interaction_risk" for s in detected_signals):
        for p in pedagogy.get_by_type("coaching_tip")[:3]:
            rec_ids.append(p.item_id)
    if any(s.get("id") == "few_examples_risk" for s in detected_signals):
        for p in pedagogy.get_by_type("rule")[:2]:
            if "example" in p.content.lower():
                rec_ids.append(p.item_id)
                break

    return FeedbackPacket(
        session_id=session_id,
        topic_id=topic_id,
        metrics=metrics,
        detected_signals=detected_signals,
        strengths=strengths,
        risks=risks,
        recommended_pedagogy_item_ids=list(dict.fromkeys(rec_ids)),
        metadata={},
    )
