"""Application service layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.application.config import get_app_config
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.session_service import SessionService
from app.application.snapshot_service import SnapshotService
from app.application.topic_service import TopicService

from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_snapshot_and_topic_services(tmp_path: Path) -> None:
    cfg = get_app_config().model_copy(
        update={
            "session_storage_dir": tmp_path / "sessions",
            "audio_storage_dir": tmp_path / "audio",
            "speech_report_dir": tmp_path / "speech_reports",
            "mode_reports_dir": tmp_path / "mode_reports",
            "group_reports_dir": tmp_path / "group_reports",
        }
    )
    snap = SnapshotService(cfg)
    rows = snap.list_snapshots()
    assert any(r.snapshot_id == "dev_snapshot_v2" for r in rows)
    top = TopicService(cfg)
    topics = top.list_topic_summaries("dev_snapshot_v2")
    assert topics


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_session_discussion_feedback_roundtrip(tmp_path: Path) -> None:
    cfg = get_app_config().model_copy(
        update={
            "session_storage_dir": tmp_path / "sessions",
            "audio_storage_dir": tmp_path / "audio",
            "speech_report_dir": tmp_path / "speech_reports",
            "mode_reports_dir": tmp_path / "mode_reports",
            "group_reports_dir": tmp_path / "group_reports",
        }
    )
    ss = SessionService(cfg)
    top = TopicService(cfg)
    tid = top.list_topic_summaries("dev_snapshot_v2")[0]["topic_id"]
    ctx = ss.create_session(
        snapshot_id="dev_snapshot_v2",
        topic_id=tid,
        user_stance="for",
        provider_name="mock",
        source="test",
    )
    disc = DiscussionService(cfg, ss)
    disc.submit_user_turn(ctx.session_id, "Hello from application test.")
    sess, rep, _ = disc.run_next_turn(ctx.session_id)
    assert sess.turns
    fb = FeedbackService(ss)
    report = fb.generate_feedback(ctx.session_id)
    assert report.text
