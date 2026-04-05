from __future__ import annotations


def test_import_learner_ui_modules() -> None:
    from app.ui.components import learner_selector  # noqa: F401
    from app.ui.components import learning_plan_panel  # noqa: F401
    from app.ui.components import progress_dashboard  # noqa: F401
    from app.ui.components import recommendation_panel  # noqa: F401
