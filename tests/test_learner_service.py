from __future__ import annotations

from pathlib import Path

from app.application.config import AppConfig
from app.application.learner_service import LearnerService
from app.application.session_service import SessionService
from app.runtime.schemas.session import SessionContext
from app.runtime.session.file_store import FileSessionStore
from app.runtime.session.manager import SessionManager


def test_create_learner_and_attach(tmp_path: Path) -> None:
    cfg = AppConfig.from_env().model_copy(
        update={
            "session_storage_dir": tmp_path / "sessions",
            "learner_storage_dir": tmp_path / "learners",
            "speech_report_dir": tmp_path / "speech",
        }
    )
    mgr = SessionManager(FileSessionStore(cfg.session_storage_dir))
    ctx = SessionContext(
        session_id="s_attach_1",
        topic_id="t1",
        phase="discussion",
        snapshot_dir=str(tmp_path / "snap"),
        runtime_profile_id="default",
        turns=[],
    )
    (tmp_path / "snap").mkdir()
    (tmp_path / "snap" / "manifest.json").write_text('{"snapshot_id":"x","schema_version":"1"}\n', encoding="utf-8")
    mgr.save(ctx)

    svc = SessionService(cfg, manager=mgr)
    lsvc = LearnerService(cfg, svc)
    lsvc.create_learner("L1", display_name="D")
    r = lsvc.attach_session_to_learner("L1", "s_attach_1", ingest=True)
    assert r["session_id"] == "s_attach_1"
    prof = lsvc.get_learner_profile("L1")
    assert prof is not None
    assert prof.total_sessions >= 1
