"""Streamlit: recommended drills for a learner."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiClient


def render_drill_panel(client: ApiClient, learner_id: str | None) -> None:
    if not learner_id:
        return
    st.subheader("Recommended drills")
    try:
        drills = client.get_learner_drills(learner_id)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Could not load drills: {exc}")
        return
    if not drills:
        st.caption("No drill recommendations.")
        return
    for d in drills[:12]:
        with st.expander(d.get("title", d.get("drill_id", "drill"))):
            st.write(d.get("objective", ""))
            st.caption(f"Skills: {', '.join(d.get('target_skills', []))}")
            st.caption(f"Why: {d.get('reason', '')}")
