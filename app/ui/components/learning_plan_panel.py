"""Learning plan steps."""

from __future__ import annotations

import os

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_learning_plan_panel(client: DiscussionApiClient, learner_id: str | None) -> None:
    if os.environ.get("ENABLE_LEARNER_UI_PANELS", "true").lower() not in ("1", "true", "yes"):
        return
    if not learner_id:
        return
    st.subheader("Learning plan")
    try:
        plan = client.get_learning_plan(learner_id)
    except ApiError as e:
        st.info(str(e))
        return
    for s in plan.get("steps") or []:
        if not isinstance(s, dict):
            continue
        st.markdown(f"**Step {s.get('order')}** — {s.get('title')}")
        st.caption(s.get("objective") or "")
