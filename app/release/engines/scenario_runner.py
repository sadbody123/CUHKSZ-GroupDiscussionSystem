"""Run canonical demo scenarios (reuses application services)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.curriculum_service import CurriculumService
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.learner_service import LearnerService
from app.application.review_service import ReviewService
from app.application.session_service import SessionService
from app.release.engines.feature_gate import is_capability_enabled, load_profile_or_default
from app.release.loaders.scenario_loader import load_demo_scenario
from app.release.schemas.scenario import DemoScenarioResult


def run_demo_scenario(
    scenario_id: str,
    *,
    profile_id: str,
    snapshot_id: str,
    topic_id: str,
    provider_name: str = "mock",
    cfg: AppConfig | None = None,
) -> DemoScenarioResult:
    cfg = cfg or get_app_config()
    profile = load_profile_or_default(profile_id)
    scenario = load_demo_scenario(scenario_id)
    now = datetime.now(timezone.utc).isoformat()
    steps_out: list[dict[str, Any]] = []
    warnings: list[str] = []
    outputs: dict[str, Any] = {}
    success = True

    for req in scenario.required_capabilities:
        if not is_capability_enabled(profile, req):
            warnings.append(f"capability disabled by profile: {req}")
            success = False

    sessions = SessionService(cfg)
    disc = DiscussionService(cfg, sessions)
    fb = FeedbackService(sessions)

    if scenario_id == "text_core_demo":
        ctx = sessions.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance="for",
            provider_name=provider_name,
            source="demo_scenario",
        )
        steps_out.append({"step": "create_session", "session_id": ctx.session_id})
        disc.submit_user_turn(ctx.session_id, "Demo user turn.")
        disc.run_next_turn(ctx.session_id)
        report = fb.generate_feedback(ctx.session_id)
        steps_out.append({"step": "feedback", "coach_report_present": bool(report.text)})
        outputs["session_id"] = ctx.session_id

    elif scenario_id == "learner_assignment_demo":
        if not is_capability_enabled(profile, "learner_analytics") or not is_capability_enabled(profile, "curriculum_delivery"):
            success = False
            warnings.append("learner or curriculum disabled")
        else:
            lsvc = LearnerService(cfg, sessions)
            lid = f"demo_learner_{uuid.uuid4().hex[:8]}"
            try:
                lsvc.create_learner(lid, display_name="Demo Learner")
            except ValueError:
                pass
            csvc = CurriculumService(cfg, sessions)
            pack = csvc.get_curriculum_pack(cfg.default_curriculum_pack_id)
            step_id = sorted(pack.steps, key=lambda x: x.order)[0].step_id if pack.steps else "step_foundation_01"
            asn = csvc.create_assignment(
                pack_id=pack.pack_id,
                learner_ids=[lid],
                created_by="demo",
                title="Demo assignment",
            )
            launch = csvc.launch_assignment_step_session(
                assignment_id=asn.assignment_id,
                pack_step_id=step_id,
                snapshot_id=snapshot_id,
                provider_name=provider_name,
                learner_id=lid,
            )
            sid = str(launch["session_id"])
            disc.submit_user_turn(sid, "Demo assignment turn.")
            disc.run_next_turn(sid)
            fb.generate_feedback(sid)
            steps_out.append({"step": "assignment_flow", "assignment_id": asn.assignment_id, "session_id": sid})
            outputs["assignment_id"] = asn.assignment_id
            outputs["session_id"] = sid

    elif scenario_id == "review_calibration_demo":
        if not is_capability_enabled(profile, "review_workspace"):
            success = False
            warnings.append("review_workspace disabled")
        else:
            ctx = sessions.create_session(
                snapshot_id=snapshot_id,
                topic_id=topic_id,
                user_stance="for",
                provider_name=provider_name,
                source="demo_review",
            )
            fb.generate_feedback(ctx.session_id)
            rsvc = ReviewService(cfg, sessions)
            pack = rsvc.create_review_pack(ctx.session_id)
            steps_out.append({"step": "review_pack", "review_pack_id": pack.review_pack_id})
            outputs["review_pack_id"] = pack.review_pack_id
            sample = cfg.project_root / "tests" / "fixtures" / "review" / "sample_manual_review.json"
            if sample.is_file():
                import json as _json

                rid = f"demo_reviewer_{uuid.uuid4().hex[:6]}"
                try:
                    rsvc.create_reviewer(reviewer_id=rid, display_name="Demo Reviewer")
                except ValueError:
                    pass
                payload = _json.loads(sample.read_text(encoding="utf-8"))
                rsvc.submit_human_review(review_pack_id=pack.review_pack_id, reviewer_id=rid, payload=payload)
                cal = rsvc.compare_ai_vs_human(pack.review_pack_id)
                steps_out.append({"step": "calibration", "overall": cal.get("overall_agreement")})
                outputs["calibration"] = cal
            else:
                warnings.append("sample_manual_review.json missing; skipped submit")

    elif scenario_id == "full_local_demo":
        sub = run_demo_scenario(
            "text_core_demo",
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
            cfg=cfg,
        )
        steps_out.append({"step": "text_core_nested", "success": sub.success})
        outputs["text_core_session_id"] = sub.outputs.get("session_id")
        success = sub.success

    else:
        success = False
        warnings.append(f"unknown scenario: {scenario_id}")

    return DemoScenarioResult(
        result_id=f"dsr_{uuid.uuid4().hex[:12]}",
        scenario_id=scenario_id,
        profile_id=profile_id,
        created_at=now,
        success=success and not any(s.get("error") for s in steps_out),
        step_results=steps_out,
        outputs=outputs,
        warnings=warnings,
        metadata={},
    )
