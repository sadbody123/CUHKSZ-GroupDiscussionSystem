"""Stability / E2E / RC status via API."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_stability_status_panel(client: DiscussionApiClient) -> None:
    st.subheader("Stability / RC")
    try:
        scenarios = client.list_e2e_scenarios()
        st.caption(f"E2E scenarios defined: {len(scenarios)}")
        rep = client.get_stability_report()
        rc = client.get_release_candidate_report()
        issues = client.list_known_issues()
        st.caption(
            f"Stability: **{rep.get('overall_status', '?')}** · "
            f"RC: **{rc.get('go_no_go', '?')}** · "
            f"Issues: {len(issues)}"
        )
        sel = st.selectbox("Run E2E scenario", [s.get("scenario_id") for s in scenarios] or ["text_core_cli"])
        if st.button("Run selected E2E via API"):
            try:
                r = client.run_e2e_scenario(sel)
                st.session_state["stability_last_e2e"] = r
            except ApiError as e:
                st.error(str(e))
        last = st.session_state.get("stability_last_e2e")
        if last:
            with st.expander("Last E2E result", expanded=False):
                st.json(last)
    except ApiError as e:
        st.warning(f"Stability endpoints: {e}")
