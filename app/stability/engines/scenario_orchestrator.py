"""Run E2E scenarios via existing release/demo + service flows."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.discussion_service import DiscussionService
from app.application.group_service import GroupService
from app.application.session_service import SessionService
from app.group_sim.constants import DEFAULT_ROSTER_TEMPLATE_ID
from app.group_sim.loaders.yaml_loader import get_roster_registry
from app.release.engines.feature_gate import is_capability_enabled, load_profile_or_default
from app.release.engines.scenario_runner import run_demo_scenario
from app.stability.engines.scenario_matrix import get_e2e_scenario, list_e2e_scenarios
from app.stability.schemas.scenario import E2ERunResult


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rid() -> str:
    return f"e2e_{uuid.uuid4().hex[:12]}"


DEMO_ALIAS: dict[str, str] = {
    "text_core_cli": "text_core_demo",
    "text_core_api": "text_core_demo",
    "learner_assignment_flow": "learner_assignment_demo",
    "review_calibration_flow": "review_calibration_demo",
    "curriculum_delivery_flow": "learner_assignment_demo",
}


def run_e2e_scenario(
    scenario_id: str,
    *,
    profile_id: str,
    snapshot_id: str,
    topic_id: str,
    provider_name: str = "mock",
    cfg: AppConfig | None = None,
    e2e_scenario_dir: Path | None = None,
) -> E2ERunResult:
    cfg = cfg or get_app_config()
    spec = get_e2e_scenario(scenario_id, extra_dir=e2e_scenario_dir)
    interface_mode = spec.interface_mode if spec else "service"
    started = _iso()
    warnings: list[str] = []
    step_results: list[dict[str, Any]] = []
    profile = load_profile_or_default(profile_id)

    for cap in (spec.required_capabilities if spec else []):
        if not is_capability_enabled(profile, cap):
            warnings.append(f"gated capability: {cap}")

    if scenario_id in DEMO_ALIAS:
        demo_id = DEMO_ALIAS[scenario_id]
        sub = run_demo_scenario(
            demo_id,
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
            cfg=cfg,
        )
        step_results.append({"step": "release_demo", "demo_scenario_id": demo_id, "success": sub.success})
        return E2ERunResult(
            run_id=_rid(),
            scenario_id=scenario_id,
            profile_id=profile_id,
            interface_mode=interface_mode,
            started_at=started,
            ended_at=_iso(),
            success=sub.success,
            step_results=step_results + sub.step_results,
            produced_artifacts={"outputs": sub.outputs},
            warnings=warnings + sub.warnings,
            metadata={"release_demo_result_id": sub.result_id},
        )

    if scenario_id == "group_mode_flow":
        if not is_capability_enabled(profile, "group_simulation"):
            return E2ERunResult(
                run_id=_rid(),
                scenario_id=scenario_id,
                profile_id=profile_id,
                interface_mode=interface_mode,
                started_at=started,
                ended_at=_iso(),
                success=True,
                step_results=[{"step": "skip", "reason": "group_simulation not enabled for profile"}],
                warnings=warnings + ["skipped: group_simulation gated"],
                metadata={"skipped": True},
            )
        sessions = SessionService(cfg)
        gsvc = GroupService(cfg, sessions)
        disc = DiscussionService(cfg, sessions)
        reg = get_roster_registry()
        rt = DEFAULT_ROSTER_TEMPLATE_ID
        tpl = reg.get(rt)
        uid = str(tpl.participants[0].get("participant_id") or "p_user") if tpl and tpl.participants else "p_user"
        ctx = sessions.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance="for",
            provider_name=provider_name,
            source="e2e_group",
        )
        ctx = gsvc.apply_roster_to_session(ctx, roster_template_id=rt, user_participant_id=uid)
        sessions.manager.save(ctx)
        disc.submit_user_turn(ctx.session_id, "E2E group user turn.")
        disc.run_next_turn(ctx.session_id)
        step_results.append({"step": "group_session", "session_id": ctx.session_id, "roster": rt})
        return E2ERunResult(
            run_id=_rid(),
            scenario_id=scenario_id,
            profile_id=profile_id,
            interface_mode=interface_mode,
            started_at=started,
            ended_at=_iso(),
            success=True,
            step_results=step_results,
            produced_artifacts={"session_id": ctx.session_id},
            warnings=warnings,
            metadata={},
        )

    if scenario_id == "audio_optional_flow":
        if not is_capability_enabled(profile, "audio_practice"):
            return E2ERunResult(
                run_id=_rid(),
                scenario_id=scenario_id,
                profile_id=profile_id,
                interface_mode=interface_mode,
                started_at=started,
                ended_at=_iso(),
                success=True,
                step_results=[{"step": "skip", "reason": "audio_practice gated"}],
                warnings=warnings + ["degraded: audio optional skipped (capability off)"],
                metadata={"degraded": True},
            )
        sessions = SessionService(cfg)
        disc = DiscussionService(cfg, sessions)
        wav = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "audio" / "sample_user_turn_01.wav"
        ctx = sessions.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance="for",
            provider_name=provider_name,
            audio_enabled=True,
            source="e2e_audio",
        )
        step_results.append({"step": "session", "session_id": ctx.session_id})
        if wav.is_file():
            from app.application.audio_service import AudioService

            audio = AudioService(cfg, sessions)
            audio.submit_user_audio_turn(ctx.session_id, wav, provider_name="mock_asr")
            disc.run_next_turn(ctx.session_id, with_tts=True, tts_provider="mock_tts")
            step_results.append({"step": "audio_turn", "ok": True})
        else:
            warnings.append("fixture wav missing; text-only path")
            disc.submit_user_turn(ctx.session_id, "E2E audio scenario (text fallback).")
            disc.run_next_turn(ctx.session_id)
        ok = True
        return E2ERunResult(
            run_id=_rid(),
            scenario_id=scenario_id,
            profile_id=profile_id,
            interface_mode=interface_mode,
            started_at=started,
            ended_at=_iso(),
            success=ok,
            step_results=step_results,
            produced_artifacts={"session_id": ctx.session_id},
            warnings=warnings,
            metadata={},
        )

    if scenario_id == "full_rc_flow":
        from app.release.engines.readiness_audit import run_readiness_audit

        rrep = run_readiness_audit(profile_id, cfg=cfg)
        step_results.append({"step": "readiness", "overall": rrep.overall_status})
        sub = run_demo_scenario(
            "text_core_demo",
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
            cfg=cfg,
        )
        step_results.append({"step": "text_core_demo", "success": sub.success})
        success = rrep.overall_status != "blocked" and sub.success
        return E2ERunResult(
            run_id=_rid(),
            scenario_id=scenario_id,
            profile_id=profile_id,
            interface_mode=interface_mode,
            started_at=started,
            ended_at=_iso(),
            success=success,
            step_results=step_results,
            produced_artifacts={"readiness": rrep.overall_status, "demo": sub.outputs},
            warnings=warnings + sub.warnings,
            metadata={},
        )

    warnings.append(f"unknown scenario_id: {scenario_id}")
    return E2ERunResult(
        run_id=_rid(),
        scenario_id=scenario_id,
        profile_id=profile_id,
        interface_mode=interface_mode,
        started_at=started,
        ended_at=_iso(),
        success=False,
        step_results=step_results,
        warnings=warnings,
        metadata={},
    )


def run_e2e_matrix(
    *,
    profile_id: str,
    snapshot_id: str,
    topic_id: str,
    provider_name: str = "mock",
    cfg: AppConfig | None = None,
    scenario_ids: list[str] | None = None,
    e2e_scenario_dir: Path | None = None,
) -> list[E2ERunResult]:
    cfg = cfg or get_app_config()
    specs = list_e2e_scenarios(e2e_scenario_dir)
    ids = scenario_ids or [s.scenario_id for s in specs]
    out: list[E2ERunResult] = []
    for sid in ids:
        out.append(
            run_e2e_scenario(
                sid,
                profile_id=profile_id,
                snapshot_id=snapshot_id,
                topic_id=topic_id,
                provider_name=provider_name,
                cfg=cfg,
                e2e_scenario_dir=e2e_scenario_dir,
            )
        )
    return out
