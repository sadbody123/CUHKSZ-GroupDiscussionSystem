"""Topic picker."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import DiscussionApiClient


def render_topic_selector(client: DiscussionApiClient, snapshot_id: str, key_prefix: str = "") -> tuple[str | None, dict | None]:
    topics = client.list_topics(snapshot_id)
    if not topics:
        st.info("No topics in this snapshot.")
        return None, None
    labels = [f"{t['topic_id']}: {t.get('topic') or ''}" for t in topics]
    idx = st.selectbox("Topic", range(len(topics)), format_func=lambda i: labels[i], key=f"{key_prefix}topic")
    tid = str(topics[idx]["topic_id"])
    detail = client.get_topic(snapshot_id, tid)
    card = detail.get("card", {})
    st.markdown(f"**Summary:** {card.get('summary') or '—'}")
    if card.get("stance_for"):
        st.caption(f"For: {card.get('stance_for')}")
    if card.get("stance_against"):
        st.caption(f"Against: {card.get('stance_against')}")
    return tid, card
