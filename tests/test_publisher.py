from __future__ import annotations

from app.application.config import AppConfig
from app.authoring.engines.publisher import publish_draft
from app.authoring.schemas.draft import AuthoringDraft


def test_publish_curriculum_custom_id(api_test_config: AppConfig) -> None:
    d = AuthoringDraft(
        draft_id="pubt",
        artifact_type="curriculum_pack",
        artifact_id="custom_pub_test",
        status="draft",
        created_at="2026-01-01T00:00:00Z",
        content={
            "pack_id": "custom_pub_test_pack_01",
            "display_name": "T",
            "steps": [
                {
                    "step_id": "s1",
                    "order": 1,
                    "title": "t",
                    "objective": "o",
                    "success_criteria": ["transcript"],
                    "focus_skills": ["x"],
                }
            ],
        },
    )
    rec = publish_draft(
        api_test_config,
        d,
        published_version="1.0.0",
        published_by="t",
        validation_report_id=None,
        preview_result_ids=[],
    )
    assert rec.output_ref
    assert "custom_pub_test_pack_01" in rec.output_ref or rec.artifact_id
