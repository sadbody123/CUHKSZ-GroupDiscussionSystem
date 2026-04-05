"""Smoke import for Streamlit mode-related components."""

from __future__ import annotations

from app.ui.components import assessment_progress_panel, debug_panel, drill_panel, mode_selector


def test_mode_ui_components_importable() -> None:
    assert mode_selector.render_mode_selector is not None
    assert drill_panel.render_drill_panel is not None
    assert assessment_progress_panel.render_assessment_progress_panel is not None
    assert debug_panel.render_debug_panel is not None
