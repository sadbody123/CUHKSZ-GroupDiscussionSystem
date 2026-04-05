from __future__ import annotations

from app.ui.components import authoring_studio_panel


def test_authoring_panel_importable() -> None:
    assert callable(authoring_studio_panel.render_authoring_studio_panel)
