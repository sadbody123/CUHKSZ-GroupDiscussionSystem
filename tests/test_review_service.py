from __future__ import annotations

from pathlib import Path

from app.application.config import AppConfig, get_app_config
from app.application.review_service import ReviewService
from app.application.session_service import SessionService


def _cfg(tmp: Path) -> AppConfig:
    return get_app_config().model_copy(
        update={
            "project_root": tmp,
            "snapshot_root": tmp / "snap",
            "session_storage_dir": tmp / "sessions",
            "audio_storage_dir": tmp / "audio",
            "speech_report_dir": tmp / "speech",
            "learner_storage_dir": tmp / "learners",
            "mode_reports_dir": tmp / "modes",
            "group_reports_dir": tmp / "groups",
            "review_storage_dir": tmp / "reviews",
            "reviewer_storage_dir": tmp / "reviewers",
        }
    )


def test_create_reviewer(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    svc = ReviewService(c, SessionService(c))
    p = svc.create_reviewer(reviewer_id="x", display_name="Y")
    assert p.reviewer_id == "x"
