"""Learner progress summary."""

from __future__ import annotations

import os

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_progress_dashboard(client: DiscussionApiClient, learner_id: str | None) -> None:
    if os.environ.get("ENABLE_LEARNER_UI_PANELS", "true").lower() not in ("1", "true", "yes"):
        return
    if not learner_id:
        return
    st.subheader("Learner progress")
    try:
        prof = client.get_learner_profile(learner_id)
        tl = client.get_learner_timeline(learner_id)
    except ApiError as e:
        st.warning(f"Could not load learner: {e}")
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Total sessions", prof.get("total_sessions", 0))
    c2.write("**Focus skills**")
    c2.write(", ".join(prof.get("current_focus_skills") or []) or "—")
    c3.write("**Weak / Strong**")
    c3.write("Weak: " + ", ".join(prof.get("weak_skills") or [])[:200])
    c3.write("Strong: " + ", ".join(prof.get("strong_skills") or [])[:200])
    pts = tl.get("points") or []
    st.caption(f"Timeline points: {len(pts)}")

