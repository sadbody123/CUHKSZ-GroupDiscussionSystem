"""Deterministic patch proposals from review / learner / curriculum signals."""

from __future__ import annotations

import uuid
from typing import Any

from app.application.config import AppConfig
from app.application.learner_service import LearnerService
from app.application.review_service import ReviewService
from app.application.session_service import SessionService
from app.authoring.constants import PATCH_SRC_CURRICULUM, PATCH_SRC_LEARNER, PATCH_SRC_REVIEW
from app.authoring.schemas.patch import PatchProposal


def generate_patches_from_review(
    cfg: AppConfig,
    sessions: SessionService,
    *,
    review_pack_id: str,
) -> list[PatchProposal]:
    rsvc = ReviewService(cfg, sessions)
    try:
        pack = rsvc.get_review_pack(review_pack_id)
    except ValueError:
        return []
    raw = pack.model_dump() if hasattr(pack, "model_dump") else {}
    sid = raw.get("session_id") or raw.get("source_session_id")
    patches: list[PatchProposal] = []
    patches.append(
        PatchProposal(
            patch_id=f"patch_{uuid.uuid4().hex[:10]}",
            source_type=PATCH_SRC_REVIEW,
            source_ref_id=review_pack_id,
            target_artifact_type="topic_card",
            target_artifact_id="tc-campus-ai",
            title="Clarify discussion pitfalls from review",
            reason="Review pack suggests reinforcing structure; add pitfalls / hints.",
            proposed_ops=[
                {
                    "op": "append_notes",
                    "path": "pedagogy_notes",
                    "value": ["Review-driven hint: cite evidence when agreeing or disagreeing."],
                }
            ],
            evidence_refs=[review_pack_id, str(sid or "")],
            confidence=0.55,
            status="proposed",
            metadata={"proxy_note": "Training curation only; not an official rubric change."},
        )
    )
    return patches


def generate_patches_from_learner(
    cfg: AppConfig,
    sessions: SessionService,
    *,
    learner_id: str,
) -> list[PatchProposal]:
    lsvc = LearnerService(cfg, sessions)
    prof = lsvc.get_learner_profile(learner_id)
    if not prof:
        return []
    weak = (prof.metadata or {}).get("weak_skills") or []
    if isinstance(weak, str):
        weak = [weak]
    skills = weak[:3] if weak else ["interaction"]
    return [
        PatchProposal(
            patch_id=f"patch_{uuid.uuid4().hex[:10]}",
            source_type=PATCH_SRC_LEARNER,
            source_ref_id=learner_id,
            target_artifact_type="drill_spec",
            target_artifact_id="micro_drill_interaction_v1",
            title="Tune drill focus from weak skills",
            reason=f"Learner analytics indicates focus on: {skills}",
            proposed_ops=[
                {"op": "set", "path": "target_skills", "value": skills},
                {"op": "append", "path": "remediation_hints", "value": ["Short replay with emphasis on " + skills[0]]},
            ],
            evidence_refs=[learner_id],
            confidence=0.5,
            status="proposed",
            metadata={"weak_skills": skills, "proxy_note": "Learner analytics are indicative only."},
        )
    ]


def generate_patches_from_curriculum_gap(
    *,
    assignment_id: str,
    completed_steps: int,
    total_steps: int,
) -> list[PatchProposal]:
    if total_steps <= 0 or completed_steps >= total_steps:
        return []
    return [
        PatchProposal(
            patch_id=f"patch_{uuid.uuid4().hex[:10]}",
            source_type=PATCH_SRC_CURRICULUM,
            source_ref_id=assignment_id,
            target_artifact_type="curriculum_pack",
            target_artifact_id="foundation_gd_pack",
            title="Emphasize next-step objectives",
            reason=f"Assignment progress {completed_steps}/{total_steps}: strengthen step clarity.",
            proposed_ops=[
                {
                    "op": "annotate_step",
                    "step_order": completed_steps + 1,
                    "path": "notes",
                    "value": ["Add facilitator note: preview success criteria before starting."],
                }
            ],
            evidence_refs=[assignment_id],
            confidence=0.45,
            status="proposed",
            metadata={},
        )
    ]


def apply_ops_to_content(content: dict[str, Any], proposed_ops: list[dict[str, Any]]) -> dict[str, Any]:
    """Minimal patch application for draft sandbox (copies dict)."""
    out = dict(content)
    for op in proposed_ops:
        kind = op.get("op")
        if kind == "set":
            parts = str(op.get("path", "")).split(".")
            cur: Any = out
            for p in parts[:-1]:
                if p not in cur or not isinstance(cur[p], dict):
                    cur[p] = {}
                cur = cur[p]
            if parts:
                cur[parts[-1]] = op.get("value")
        elif kind == "append":
            path = str(op.get("path", ""))
            val = op.get("value")
            if path in out and isinstance(out[path], list) and val is not None:
                out[path] = list(out[path]) + ([val] if not isinstance(val, list) else val)
        elif kind == "append_notes":
            notes = out.setdefault("notes", [])
            if isinstance(notes, list) and isinstance(op.get("value"), list):
                notes.extend(op["value"])
    return out
