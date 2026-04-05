from __future__ import annotations

from app.ui.components import curriculum_pack_selector


def test_curriculum_pack_selector_session_key() -> None:
    assert curriculum_pack_selector.SS_CURRICULUM_PACK_ID == "ui_curriculum_pack_id"
