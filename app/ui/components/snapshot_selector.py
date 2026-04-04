"""Snapshot picker."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import DiscussionApiClient


def render_snapshot_selector(client: DiscussionApiClient, key_prefix: str = "") -> str | None:
    snaps = client.list_snapshots()
    if not snaps:
        st.warning("No snapshots found under the server snapshot root.")
        return None
    labels = [f"{s['snapshot_id']} — topics: {s.get('topic_card_count', 0)}" for s in snaps]
    idx = st.selectbox("Snapshot", range(len(snaps)), format_func=lambda i: labels[i], key=f"{key_prefix}snap")
    return str(snaps[idx]["snapshot_id"])
