"""Tests for runtime V2 facade."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.agent_runtime_v2.facade.discussion_runtime import AgentRuntimeFacade
from app.application.config import AppConfig, get_app_config
from app.application.session_service import SessionService
from app.runtime.schemas.agent import AgentReply
from tests.conftest import HAS_SNAPSHOT_V2

pytestmark = pytest.mark.v2_graph


def _test_config(tmp_path: Path) -> AppConfig:
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


def test_facade_run_next_turn_uses_graph_shell(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = _test_config(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.manager.create_session(
        topic_id="tc-any",
        snapshot_dir=str(tmp_path),
        provider_name="mock",
        runtime_profile_id="default",
    )
    facade = AgentRuntimeFacade(cfg, ss)
    monkeypatch.setattr("app.agent_runtime_v2.facade.discussion_runtime.has_langgraph_support", lambda: True)

    def _fake_run(state, *, max_steps=None):
        sess = ss.manager.load(ctx.session_id)
        assert sess is not None
        state.next_actor = "ally"
        return state, sess, AgentReply(role="ally", text="mock-v2-reply"), [AgentReply(role="ally", text="mock-v2-reply")]

    monkeypatch.setattr(facade._graph, "run", _fake_run)
    sess, reply, _ = facade.run_next_turn(ctx.session_id)
    assert sess.session_id == ctx.session_id
    assert reply is not None
    assert reply.text == "mock-v2-reply"


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_facade_run_one_step_with_real_snapshot(tmp_path: Path) -> None:
    cfg = _test_config(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.create_session(
        snapshot_id="dev_snapshot_v2",
        topic_id="tc-campus-ai",
        user_stance="for",
        provider_name="mock",
        runtime_profile_id="default",
        source="test",
    )
    from app.application.discussion_service import DiscussionService

    DiscussionService(cfg, ss).submit_user_turn(ctx.session_id, "Testing runtime v2 one step.")
    facade = AgentRuntimeFacade(cfg, ss)
    sess, reply, _next = facade.run_next_turn(ctx.session_id)
    assert sess.turns
    assert reply is not None
