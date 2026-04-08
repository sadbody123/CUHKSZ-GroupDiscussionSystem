"""Application/runtime review service tests for V2 workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.application.config import AppConfig, get_app_config
from app.application.discussion_service import DiscussionService
from app.application.runtime_review_service import RuntimeReviewService
from app.application.session_service import SessionService
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.transcript import TranscriptTurn

pytestmark = pytest.mark.v2_graph


def _cfg(tmp_path: Path) -> AppConfig:
    return get_app_config().model_copy(
        update={
            "session_storage_dir": tmp_path / "sessions",
            "audio_storage_dir": tmp_path / "audio",
            "speech_report_dir": tmp_path / "speech_reports",
            "mode_reports_dir": tmp_path / "mode_reports",
            "group_reports_dir": tmp_path / "group_reports",
            "agent_runtime_backend": "v2",
            "agent_runtime_v2_dir": tmp_path / "runtime_v2",
        }
    )


def _prepare_interrupted_review(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg = _cfg(tmp_path)
    sessions = SessionService(cfg)
    disc = DiscussionService(cfg, sessions)
    svc = RuntimeReviewService(cfg, sessions)
    ctx = sessions.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")

    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.select_next_actor", lambda state, session: "ally")

    def _gen(state, session):
        session.turns.append(
            TranscriptTurn(
                turn_id=f"ally-{len(session.turns)+1}",
                speaker_role="ally",
                text="bad",
                created_at="2026-01-01T00:00:00Z",
            )
        )
        return session, AgentReply(role="ally", text="bad")

    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.generate_turn", _gen)
    monkeypatch.setattr(
        "app.agent_runtime_v2.graphs.discussion_graph.quality_check",
        lambda state, session, reply, **kwargs: "interrupt",
    )
    disc.auto_run_discussion(ctx.session_id, max_steps=1, auto_fill_user=False)
    pending = svc.list_pending_reviews()
    assert pending
    return cfg, sessions, svc, pending[0]


def test_runtime_review_service_query_and_transitions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _cfg_v2, _sessions, svc, review = _prepare_interrupted_review(tmp_path, monkeypatch)
    rid = review["review_id"]
    got = svc.get_review(rid)
    assert got is not None
    assert got["status"] == "pending"

    approved = svc.approve_review(rid, action="approve", expected_version=got["version"], updated_by="teacher_a")
    assert approved["status"] == "approved"
    with pytest.raises(ValueError):
        svc.reject_review(rid, reason="late reject", expected_version=approved["version"], updated_by="teacher_b")


def test_apply_edited_draft_concurrency_and_controlled_persist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _cfg_v2, sessions, svc, review = _prepare_interrupted_review(tmp_path, monkeypatch)
    rid = review["review_id"]
    before = sessions.manager.load(review["session_id"])
    assert before is not None
    assert len(before.turns) == 0

    with pytest.raises(ValueError):
        svc.apply_edited_draft(
            rid,
            edited_text="Manual correction",
            expected_version=999,
            updated_by="teacher_a",
        )

    out = svc.apply_edited_draft(
        rid,
        edited_text="Manual correction with explicit relevance.",
        expected_version=review["version"],
        updated_by="teacher_a",
        note="human rewrite",
        resume_after_apply=False,
    )
    assert out["applied_turn_id"]
    after = sessions.manager.load(review["session_id"])
    assert after is not None
    assert len(after.turns) == 1
    assert after.turns[-1].metadata.get("manual_override") is True


def test_resume_from_review_and_metrics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _cfg_v2, _sessions, svc, review = _prepare_interrupted_review(tmp_path, monkeypatch)
    rid = review["review_id"]
    # approve first, then resume
    svc.approve_review(rid, action="approve", expected_version=review["version"], updated_by="teacher_a")
    out = svc.resume_from_review(rid, additional_steps=1)
    assert "turn_count" in out
    m = svc.get_metrics()
    assert m["created_review_count"] >= 1
    assert m["pending_review_count"] >= 0
