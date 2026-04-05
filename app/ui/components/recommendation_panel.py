"""Recommendation list."""

from __future__ import annotations

import os

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_recommendation_panel(client: DiscussionApiClient, learner_id: str | None) -> None:
    if os.environ.get("ENABLE_LEARNER_UI_PANELS", "true").lower() not in ("1", "true", "yes"):
        return
    if not learner_id:
        return
    st.subheader("Recommendations")
    try:
        items = client.get_learner_recommendations(learner_id)
    except ApiError as e:
        st.info(str(e))
        return
    for it in items[:20]:
        st.markdown(f"**[{it.get('recommendation_type')}]** {it.get('title')}")
        st.caption(it.get("reason") or "")

