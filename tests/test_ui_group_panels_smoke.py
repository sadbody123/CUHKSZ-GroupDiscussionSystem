"""Smoke import for group simulation UI components."""

from __future__ import annotations

from app.ui.components import roster_selector, speaking_balance_panel, team_layout_panel


def test_group_ui_imports() -> None:
    assert roster_selector.render_roster_selector is not None
    assert team_layout_panel.render_team_layout_panel is not None
    assert speaking_balance_panel.render_speaking_balance_panel is not None
