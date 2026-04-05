"""Streamlit Web MVP — talks to FastAPI via DiscussionApiClient."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient
from app.ui.components import audio_player_panel, audio_upload_panel
from app.ui.components import delivery_feedback_panel, speech_metrics_panel
from app.ui.components import (
    assessment_progress_panel,
    controls_panel,
    debug_panel,
    drill_panel,
    session_panel,
    snapshot_selector,
    speaking_balance_panel,
    team_layout_panel,
    topic_selector,
)
from app.ui.components import learner_selector, learning_plan_panel, progress_dashboard, recommendation_panel
from app.ui.components import final_delivery_panel, release_readiness_panel, retrieval_status_panel, stability_status_panel, system_info_panel
from app.ui.components import reviewer_selector, review_queue_panel, review_workspace_panel
from app.ui.components import curriculum_pack_selector, assignment_panel, assignment_progress_panel
from app.ui.components import authoring_studio_panel
from app.ui.components import feedback_panel as fb_panel
from app.ui.components import transcript_panel
from app.ui.config import get_ui_config
from app.ui import state as ststate


def _client() -> DiscussionApiClient:
    cfg = get_ui_config()
    return DiscussionApiClient(cfg.api_base_url)


def main() -> None:
    st.set_page_config(page_title="Group Discussion", layout="wide")
    st.title("CUHKSZ Group Discussion (MVP)")
    st.caption(
        "Training / advisory prototype — outputs are heuristic, simulated, or proxy metrics unless stated; "
        "not an official assessment, exam, or certification. Prefer provider **mock** for repeatable demos."
    )

    cfg = get_ui_config()
    st.caption(f"API: {cfg.api_base_url}")

    client = _client()
    health: dict | None = None
    try:
        health = client.get_health()
        st.sidebar.success(
            f"API {health.get('app_version') or health.get('version', '?')} — "
            f"provider: {health.get('default_provider')}"
        )
    except ApiError as e:
        st.sidebar.error(f"Cannot reach API: {e}. Start the API or check UI_API_BASE_URL.")

    if ststate.SS_SNAPSHOT_ID not in st.session_state:
        st.session_state[ststate.SS_SNAPSHOT_ID] = None
    if ststate.SS_SESSION_ID not in st.session_state:
        st.session_state[ststate.SS_SESSION_ID] = None
    if ststate.SS_LEARNER_ID not in st.session_state:
        st.session_state[ststate.SS_LEARNER_ID] = None

    session_id = st.session_state.get(ststate.SS_SESSION_ID)
    reviewer_id = reviewer_selector.render_reviewer_selector(client) if health else None
    learner_id = st.session_state.get(ststate.SS_LEARNER_ID)
    pack_id = curriculum_pack_selector.render_curriculum_pack_selector(client) if health else None

    def refresh() -> None:
        st.rerun()

    status = None
    if session_id:
        try:
            status = client.get_session(session_id)
        except ApiError:
            status = None

    if not health:
        st.warning("API unavailable — start the server with `python main.py run-api` or fix UI_API_BASE_URL.")
    else:
        col_left, col_right = st.columns([1, 2])

        with col_left:
            learner_selector.render_learner_selector(client)
            with st.expander("Authoring Studio", expanded=False):
                authoring_studio_panel.render_authoring_studio_panel(
                    client,
                    snapshot_id=st.session_state.get(ststate.SS_SNAPSHOT_ID),
                )
            assignment_panel.render_assignment_panel(client, learner_id, pack_id)
            drill_panel.render_drill_panel(client, learner_id)
            st.subheader("1. Snapshot & topic")
            snap = snapshot_selector.render_snapshot_selector(client)
            if snap:
                st.session_state[ststate.SS_SNAPSHOT_ID] = snap
                topic_id, _card = topic_selector.render_topic_selector(client, snap)
                if topic_id:
                    session_panel.render_session_creator(client, snap, topic_id)

        with col_right:
            review_queue_panel.render_review_queue_panel(client, session_id)
            review_workspace_panel.render_review_workspace_panel(client, session_id, reviewer_id)
            assignment_progress_panel.render_assignment_progress_panel(
                client,
                snapshot_id=st.session_state.get(ststate.SS_SNAPSHOT_ID),
                learner_id=learner_id,
            )
            progress_dashboard.render_progress_dashboard(client, learner_id)
            recommendation_panel.render_recommendation_panel(client, learner_id)
            learning_plan_panel.render_learning_plan_panel(client, learner_id)
            if session_id and status:
                assessment_progress_panel.render_assessment_progress_panel(status)
                team_layout_panel.render_team_layout_panel(status)
                speaking_balance_panel.render_speaking_balance_panel(client, session_id)
                transcript_panel.render_transcript(status.get("latest_turns") or [])
                audio_upload_panel.render_audio_upload_panel(client, session_id, on_refresh=refresh)
                audio_player_panel.render_audio_player_panel(client, session_id)
                speech_metrics_panel.render_speech_metrics_panel(
                    client,
                    session_id,
                    status.get("latest_turns") or [],
                    on_refresh=refresh,
                )
                delivery_feedback_panel.render_delivery_feedback_panel(client, session_id)
                controls_panel.render_controls(client, session_id, on_refresh=refresh)
                st.divider()
                if status.get("coach_report_present") and status.get("coach_text_preview"):
                    st.subheader("Coach report")
                    st.write(status.get("coach_text_preview"))
                else:
                    fb_panel.render_feedback_panel(client, status)
                if status.get("coach_report_present"):
                    fb_panel.render_mode_report_only(client, status)
            elif session_id:
                st.warning("Session not found — create a new one.")
            else:
                st.info("Create a session to start.")

    review_summary = None
    if health and session_id:
        try:
            review_summary = client.get_session_review_summary(session_id)
        except ApiError:
            review_summary = None

    rec_n = None
    plan_id = None
    if health and learner_id:
        try:
            rec_n = len(client.get_learner_recommendations(learner_id))
            plan_id = str(client.get_learning_plan(learner_id).get("plan_id") or "")
        except ApiError:
            pass

    rel_prof_id = None
    readiness_st = None
    cap_n = None
    demo_ok = None
    vis = None
    auth_gated = None
    stab_st = None
    rc_go = None
    issue_n = None
    h_acc_p = None
    h_acc_f = None
    h_lim = None
    h_docs = None
    if health:
        try:
            rp = client.get_active_release_profile()
            rel_prof_id = str(rp.get("profile_id") or "")
            try:
                frs = client.get_final_release_summary()
                h_acc_p = frs.get("acceptance_passed")
                h_acc_f = frs.get("acceptance_failed")
                h_lim = frs.get("accepted_limitations_count")
                h_docs = frs.get("docs_bundle_enabled")
            except ApiError:
                pass
            rr = client.get_system_readiness()
            readiness_st = str(rr.get("overall_status") or "")
            cap_n = len(client.get_system_capabilities())
            vis = client.get_release_visibility()
            ui_pol = vis.get("ui_visibility_policy") or {}
            auth_gated = not bool(ui_pol.get("authoring_studio", True))
            last = st.session_state.get("release_last_demo_result")
            if isinstance(last, dict):
                demo_ok = bool(last.get("success"))
            srep = client.get_stability_report()
            stab_st = str(srep.get("overall_status") or "")
            rc_go = str(client.get_release_candidate_report().get("go_no_go") or "")
            issue_n = len(client.list_known_issues())
        except ApiError:
            pass

    with st.sidebar:
        if health:
            with st.expander("Final delivery", expanded=False):
                final_delivery_panel.render_final_delivery_panel(client)
            with st.expander("Stability / RC", expanded=False):
                stability_status_panel.render_stability_status_panel(client)
            with st.expander("Release / readiness", expanded=False):
                release_readiness_panel.render_release_readiness_panel(
                    client,
                    snapshot_id=st.session_state.get(ststate.SS_SNAPSHOT_ID),
                )
        system_info_panel.render_system_info_panel(client)
        retrieval_status_panel.render_retrieval_status_panel(
            client,
            snapshot_id=st.session_state.get(ststate.SS_SNAPSHOT_ID),
            session_status=status,
        )
        debug_panel.render_debug_panel(
            status,
            api_base_url=cfg.api_base_url,
            app_version=(health or {}).get("app_version") or (health or {}).get("version"),
            snapshot_id=st.session_state.get(ststate.SS_SNAPSHOT_ID),
            session_id=st.session_state.get(ststate.SS_SESSION_ID),
            learner_id=learner_id,
            recommendation_count=rec_n,
            plan_id=plan_id or None,
            mode_status=status,
            review_summary=review_summary,
            release_profile_id=rel_prof_id,
            readiness_status=readiness_st,
            capability_count=cap_n,
            demo_scenario_last_success=demo_ok,
            authoring_panel_gated=auth_gated,
            stability_status=stab_st,
            rc_go_no_go=rc_go,
            known_issue_count=issue_n,
            handover_acceptance_passed=h_acc_p,
            handover_acceptance_failed=h_acc_f,
            accepted_limitations_count=h_lim,
            final_delivery_docs_enabled=h_docs,
        )


if __name__ == "__main__":
    main()
