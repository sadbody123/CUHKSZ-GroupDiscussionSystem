"""Streamlit: mode / assessment simulation progress (soft timer / phases)."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_assessment_progress_panel(status: dict[str, Any] | None) -> None:
    """Uses session status from GET /sessions/{id} (includes mode + timer_state)."""
    if not status:
        return
    st.subheader("Mode / assessment (simulation)")
    note = status.get("simulation_note")
    if note:
        st.info(note)
    st.write(
        f"**Mode:** `{status.get('mode_id') or '—'}` · "
        f"**Preset:** `{status.get('preset_id') or '—'}` · "
        f"**Drill:** `{status.get('drill_id') or '—'}` · "
        f"**Template:** `{status.get('assessment_template_id') or '—'}`"
    )
    st.caption(f"Discussion phase: **{status.get('phase')}**")
    timer = status.get("timer_state") or {}
    if timer:
        est = timer.get("assessment_phase_estimate")
        line = (
            f"Elapsed ~{timer.get('elapsed_seconds', 0)}s"
            + (f" · estimated assessment phase: **{est}**" if est else "")
        )
        if timer.get("remaining_in_phase_seconds") is not None:
            line += f" · remaining in phase ~{timer['remaining_in_phase_seconds']}s"
        st.caption(line)
    mode_state = status.get("mode_state") or {}
    events = list(mode_state.get("constraint_events") or [])
    if events:
        st.caption("Recent constraint hints:")
        for ev in events[-5:]:
            st.caption(f"• [{ev.get('type', 'event')}] {ev.get('detail', '')}")
