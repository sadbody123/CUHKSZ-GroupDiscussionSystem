from __future__ import annotations

from app.authoring.engines.validator import run_validation
from app.authoring.schemas.draft import AuthoringDraft


def test_validate_curriculum_draft_ok() -> None:
    d = AuthoringDraft(
        draft_id="v1",
        artifact_type="curriculum_pack",
        artifact_id="p",
        status="draft",
        created_at="2026-01-01T00:00:00Z",
        content={
            "pack_id": "custom_pack_x",
            "display_name": "X",
            "steps": [
                {
                    "step_id": "s1",
                    "order": 1,
                    "title": "t",
                    "objective": "o",
                    "success_criteria": ["transcript"],
                    "focus_skills": ["discussion_language"],
                }
            ],
        },
    )
    rep = run_validation(d)
    assert rep.valid
