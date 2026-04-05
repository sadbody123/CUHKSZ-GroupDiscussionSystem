"""Debug / status sidebar."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_debug_panel(
    status: dict[str, Any] | None,
    *,
    api_base_url: str | None = None,
    app_version: str | None = None,
    snapshot_id: str | None = None,
    session_id: str | None = None,
    learner_id: str | None = None,
    recommendation_count: int | None = None,
    plan_id: str | None = None,
    mode_status: dict[str, Any] | None = None,
    review_summary: dict[str, Any] | None = None,
    release_profile_id: str | None = None,
    readiness_status: str | None = None,
    capability_count: int | None = None,
    demo_scenario_last_success: bool | None = None,
    authoring_panel_gated: bool | None = None,
    stability_status: str | None = None,
    rc_go_no_go: str | None = None,
    known_issue_count: int | None = None,
    handover_acceptance_passed: int | None = None,
    handover_acceptance_failed: int | None = None,
    accepted_limitations_count: int | None = None,
    final_delivery_docs_enabled: bool | None = None,
) -> None:
    st.subheader("Debug")
    if api_base_url:
        st.caption(f"API base URL: {api_base_url}")
    if app_version:
        st.caption(f"App version: {app_version}")
    if snapshot_id:
        st.caption(f"Snapshot id: {snapshot_id}")
    if session_id:
        st.caption(f"Session id: {session_id}")
    if learner_id:
        st.caption(f"Learner id: {learner_id}")
    if recommendation_count is not None:
        st.caption(f"Recommendation count: {recommendation_count}")
    if plan_id:
        st.caption(f"Plan id: {plan_id}")
    if stability_status:
        st.caption(f"Stability: {stability_status}")
    if rc_go_no_go:
        st.caption(f"RC go/no-go: {rc_go_no_go}")
    if known_issue_count is not None:
        st.caption(f"Known issues (tracked): {known_issue_count}")
    if handover_acceptance_passed is not None:
        st.caption(f"Handover acceptance passed checks: {handover_acceptance_passed}")
    if handover_acceptance_failed is not None:
        st.caption(f"Handover acceptance failed checks: {handover_acceptance_failed}")
    if accepted_limitations_count is not None:
        st.caption(f"Accepted limitations (evidence): {accepted_limitations_count}")
    if final_delivery_docs_enabled is not None:
        st.caption(f"Final delivery docs bundle (UI flag): {final_delivery_docs_enabled}")
    if not status:
        st.caption("No session loaded.")
        return
    ms = mode_status or status
    timer = ms.get("timer_state") or {}
    mstate = ms.get("mode_state") or {}
    ce = mstate.get("constraint_events") or []
    payload = {
        "session_id": status.get("session_id"),
        "phase": status.get("phase"),
        "mode_id": ms.get("mode_id"),
        "preset_id": ms.get("preset_id"),
        "drill_id": ms.get("drill_id"),
        "assessment_template_id": ms.get("assessment_template_id"),
        "mode_report_id": status.get("mode_report_id"),
        "runtime_profile_id": status.get("runtime_profile_id"),
        "provider": status.get("provider_name"),
        "turn_count": status.get("turn_count"),
        "coach_report": status.get("coach_report_present"),
        "peek_next": status.get("peek_next_role"),
        "audio_enabled": status.get("audio_enabled"),
        "asr_provider": status.get("asr_provider_name"),
        "tts_provider": status.get("tts_provider_name"),
        "audio_asset_count": status.get("audio_asset_count"),
        "speech_report_id": status.get("speech_report_id"),
        "speech_analysis_enabled": status.get("speech_analysis_enabled"),
        "timer_kind": timer.get("kind"),
        "constraint_event_count": len(ce),
        "roster_template_id": ms.get("roster_template_id"),
        "user_participant_id": ms.get("user_participant_id"),
        "group_balance_report_id": ms.get("group_balance_report_id"),
        "next_candidate_participant_ids": ms.get("next_candidate_participant_ids"),
        "curriculum_pack_id": status.get("curriculum_pack_id"),
        "assignment_id": status.get("assignment_id"),
        "assignment_step_id": status.get("assignment_step_id"),
    }
    if review_summary:
        payload["review_pack_count"] = review_summary.get("pack_count")
        payload["review_submission_count"] = review_summary.get("review_count")
    if release_profile_id:
        payload["release_profile_id"] = release_profile_id
    if readiness_status:
        payload["readiness_status"] = readiness_status
    if capability_count is not None:
        payload["capability_count"] = capability_count
    if demo_scenario_last_success is not None:
        payload["demo_scenario_last_success"] = demo_scenario_last_success
    if authoring_panel_gated is not None:
        payload["authoring_panel_gated_by_release"] = authoring_panel_gated
    st.json(payload)
