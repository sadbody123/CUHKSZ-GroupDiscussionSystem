"""Final release / handover summary via API."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_final_delivery_panel(client: DiscussionApiClient) -> None:
    st.subheader("Final delivery")
    try:
        s = client.get_final_release_summary()
        st.caption(
            f"RC: **{s.get('rc_go_no_go', '?')}** · readiness: **{s.get('readiness_status', '?')}** · "
            f"stability: **{s.get('stability_overall', '?')}**"
        )
        st.caption(
            f"Acceptance passed/failed checks: {s.get('acceptance_passed', 0)}/{s.get('acceptance_failed', 0)} · "
            f"tracked issues: {s.get('known_issues_count', 0)}"
        )
        if st.button("Run verify-delivery (API)"):
            try:
                r = client.post_verify_delivery()
                st.session_state["last_verify_delivery"] = r
            except ApiError as e:
                st.error(str(e))
        last = st.session_state.get("last_verify_delivery")
        if last:
            with st.expander("Last verification", expanded=False):
                st.json(last)
    except ApiError as e:
        st.warning(f"Final delivery API: {e}")
