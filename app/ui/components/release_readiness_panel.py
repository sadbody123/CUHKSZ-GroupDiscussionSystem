"""Release profile, readiness, and demo scenario (API-driven)."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_release_readiness_panel(client: DiscussionApiClient, *, snapshot_id: str | None) -> None:
    st.subheader("Release & readiness")
    try:
        prof = client.get_active_release_profile()
        vis = client.get_release_visibility()
        caps = client.get_system_capabilities()
        rep = client.get_system_readiness()
    except ApiError as e:
        st.warning(f"Release endpoints unavailable: {e}")
        return

    pid = prof.get("profile_id") or "?"
    st.caption(f"Active profile: **{pid}** · gating: {vis.get('gating_enabled')}")
    ex = prof.get("experimental_capabilities") or []
    dis = prof.get("disabled_capabilities") or []
    st.caption(f"Capabilities loaded: {len(caps)} · experimental flags: {len(ex)}")
    with st.expander("Enabled / experimental / disabled (profile)", expanded=False):
        st.json({"enabled_capabilities": prof.get("enabled_capabilities"), "experimental": ex, "disabled": dis})

    status = rep.get("overall_status") or "?"
    st.caption(f"Readiness: **{status}**")
    if rep.get("summary"):
        st.json({"summary": rep.get("summary"), "recommended_actions": rep.get("recommended_actions")})

    snap = snapshot_id or "dev_snapshot_v2"
    scen = st.selectbox(
        "Demo scenario",
        ["text_core_demo", "learner_assignment_demo", "review_calibration_demo", "full_local_demo"],
        key="release_demo_scenario_select",
    )
    if st.button("Run demo scenario (API)", key="release_run_demo"):
        try:
            res = client.run_system_demo_scenario(scen, snapshot_id=snap, topic_id="tc-campus-ai")
            st.session_state["release_last_demo_result"] = res
        except ApiError as e:
            st.error(str(e))
    last = st.session_state.get("release_last_demo_result")
    if last:
        st.caption(f"Last run success: {last.get('success')}")
        with st.expander("Last demo result", expanded=False):
            st.json(last)


def panel_gated_for_profile(visibility: dict, panel_key: str) -> bool:
    """Return True if UI policy hides this panel key (best-effort)."""
    ui = visibility.get("ui_visibility_policy") or {}
    if panel_key in ui:
        return not bool(ui[panel_key])
    return False
