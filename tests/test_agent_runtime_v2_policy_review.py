"""Policy and review workflow tests for runtime V2."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.agent_runtime_v2.facade.discussion_runtime import AgentRuntimeFacade
from app.agent_runtime_v2.policy.quality_policy import QualityPolicyResolver
from app.application.config import AppConfig, get_app_config
from app.application.discussion_service import DiscussionService
from app.application.session_service import SessionService
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.transcript import TranscriptTurn


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


def test_quality_policy_resolves_from_profiles() -> None:
    r = QualityPolicyResolver()
    p_default = r.resolve("default", role="ally")
    p_concise = r.resolve("concise", role="ally")
    assert p_default.min_reply_length >= 30
    assert p_default.max_repairs == 1
    assert p_concise.min_reply_length == 20
    assert p_concise.enable_interrupt is False


def test_interrupt_creates_review_item_and_status_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ds = DiscussionService(cfg, ss)
    facade = ds._v2_runtime  # type: ignore[attr-defined]
    assert facade is not None
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")

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
    _sess, _replies = ds.auto_run_discussion(ctx.session_id, max_steps=1, auto_fill_user=False)

    pending = facade.list_pending_reviews()
    assert pending
    review_id = pending[0]["review_id"]
    got = facade.get_review(review_id)
    assert got is not None
    assert got["status"] == "pending"
    approved = facade.approve_review(review_id, action="approve")
    assert approved["status"] == "approved"


def test_resume_from_review_and_draft_persist_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ds = DiscussionService(cfg, ss)
    facade = ds._v2_runtime  # type: ignore[attr-defined]
    assert facade is not None
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")

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
    _sess, _replies = ds.auto_run_discussion(ctx.session_id, max_steps=1, auto_fill_user=False)

    # draft boundary: interrupted draft turn should not be persisted to store.
    persisted = ss.manager.load(ctx.session_id)
    assert persisted is not None
    assert len(persisted.turns) == 0

    review_id = facade.list_pending_reviews()[0]["review_id"]
    monkeypatch.setattr(
        "app.agent_runtime_v2.graphs.discussion_graph.quality_check",
        lambda state, session, reply, **kwargs: "pass",
    )
    out = facade.resume_from_review(review_id, additional_steps=1)
    assert out["turn_count"] >= 1
