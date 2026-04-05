from __future__ import annotations

from app.ui.components import reviewer_selector


def test_reviewer_session_state_key_defined() -> None:
    assert reviewer_selector.SS_REVIEWER_ID == "ui_reviewer_id"
