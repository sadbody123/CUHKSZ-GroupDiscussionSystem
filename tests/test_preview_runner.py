from __future__ import annotations

from app.application.config import AppConfig
from app.authoring.engines.preview_runner import run_preview
from app.authoring.schemas.draft import AuthoringDraft


def test_artifact_render_preview(api_test_config: AppConfig) -> None:
    d = AuthoringDraft(
        draft_id="p1",
        artifact_type="curriculum_pack",
        artifact_id="x",
        status="draft",
        created_at="2026-01-01T00:00:00Z",
        content={"pack_id": "x", "display_name": "D", "steps": []},
    )
    r = run_preview(
        api_test_config,
        d,
        preview_kind="artifact_render",
        snapshot_id=None,
        provider_name="mock",
        learner_id=None,
    )
    assert r.success
    assert "rendered_keys" in r.summary
