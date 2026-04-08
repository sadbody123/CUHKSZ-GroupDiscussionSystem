"""Integration-oriented tests for compiled runtime V2 graph."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.agent_runtime_v2.facade.discussion_runtime import AgentRuntimeFacade
from app.agent_runtime_v2.graphs.discussion_graph import DiscussionGraph
from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.agent_runtime_v2.store.checkpoint_store import FileCheckpointStore
from app.agent_runtime_v2.store.event_logger import RuntimeEventLogger
from app.agent_runtime_v2.tools.session_tool import SessionTool
from app.application.config import AppConfig, get_app_config
from app.application.discussion_service import DiscussionService
from app.application.exceptions import SessionNotFoundError
from app.application.session_service import SessionService
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.transcript import TranscriptTurn
from tests.conftest import HAS_SNAPSHOT_V2

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


def test_compiled_graph_builds_when_langgraph_available(tmp_path: Path) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    graph = DiscussionGraph(
        session_tool=SessionTool(ss),
        event_logger=RuntimeEventLogger(cfg.agent_runtime_v2_dir / "events" / "runtime_v2_events.jsonl"),
    )
    compiled = graph.build_compiled_graph()
    assert hasattr(compiled, "invoke")


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_v2_run_next_turn_creates_checkpoint_and_event(tmp_path: Path) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.create_session(
        snapshot_id="dev_snapshot_v2",
        topic_id="tc-campus-ai",
        user_stance="for",
        provider_name="mock",
        source="test",
    )
    ds = DiscussionService(cfg, ss)
    ds.submit_user_turn(ctx.session_id, "Graph runtime v2 test.")
    sess, reply, _ = ds.run_next_turn(ctx.session_id)
    assert sess.turns
    assert reply is not None

    ckpt_dir = cfg.agent_runtime_v2_dir / "checkpoints"
    evt_file = cfg.agent_runtime_v2_dir / "events" / "runtime_v2_events.jsonl"
    assert ckpt_dir.exists()
    assert any(ckpt_dir.glob("*.json"))
    assert evt_file.is_file()


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_run_next_turn_equals_auto_run_one_step(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    monkeypatch.setattr(
        "app.agent_runtime_v2.graphs.discussion_graph.select_next_actor",
        lambda state, session: "ally",
    )

    ss_a = SessionService(cfg)
    ctx_a = ss_a.create_session(
        snapshot_id="dev_snapshot_v2",
        topic_id="tc-campus-ai",
        user_stance="for",
        provider_name="mock",
        source="test",
    )
    ds_a = DiscussionService(cfg, ss_a)
    ds_a.submit_user_turn(ctx_a.session_id, "Compare single-step path.")
    sess_a, rep_a, _ = ds_a.run_next_turn(ctx_a.session_id)

    ss_b = SessionService(cfg)
    ctx_b = ss_b.create_session(
        snapshot_id="dev_snapshot_v2",
        topic_id="tc-campus-ai",
        user_stance="for",
        provider_name="mock",
        source="test",
    )
    ds_b = DiscussionService(cfg, ss_b)
    ds_b.submit_user_turn(ctx_b.session_id, "Compare single-step path.")
    sess_b, reps_b = ds_b.auto_run_discussion(ctx_b.session_id, max_steps=1, auto_fill_user=False)

    assert len(sess_a.turns) == len(sess_b.turns)
    assert rep_a is not None
    assert len(reps_b) == 1
    assert sess_a.turns[-1].speaker_role == sess_b.turns[-1].speaker_role


def test_auto_run_discussion_uses_graph_loop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")
    ds = DiscussionService(cfg, ss)

    counter = {"n": 0}

    def _fake_select_next_actor(state, session):
        counter["n"] += 1
        state.next_actor = "ally"
        return "ally"

    def _fake_generate_turn(state, session):
        tid = f"ally-{len(session.turns)+1}"
        session.turns.append(
            TranscriptTurn(
                turn_id=tid,
                speaker_role="ally",
                text="loop-turn",
                created_at="2026-01-01T00:00:00Z",
            )
        )
        state.last_role = "ally"
        return session, AgentReply(role="ally", text="loop-turn")

    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.select_next_actor", _fake_select_next_actor)
    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.generate_turn", _fake_generate_turn)
    monkeypatch.setattr(
        "app.agent_runtime_v2.graphs.discussion_graph.quality_check",
        lambda state, session, reply, **kwargs: "pass",
    )

    sess, replies = ds.auto_run_discussion(ctx.session_id, max_steps=3, auto_fill_user=False)
    assert len(replies) == 3
    assert counter["n"] >= 3
    assert len(sess.turns) == 3
    payload = FileCheckpointStore(cfg.agent_runtime_v2_dir / "checkpoints").load_latest_for_session(ctx.session_id)
    assert payload is not None
    assert payload.get("status") == "interrupted"
    assert (payload.get("state") or {}).get("stop_reason") == "max_steps_reached"


def test_resume_run_checkpoint_behaviors(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")
    facade = AgentRuntimeFacade(cfg, ss)
    store = FileCheckpointStore(cfg.agent_runtime_v2_dir / "checkpoints")

    completed = DiscussionGraphState.from_session(
        ctx, run_id="run-completed", max_steps=1, trace_id="trace-run-completed"
    )
    completed.run_status = "completed"
    completed.stop_reason = "completed"
    store.save(completed, status="completed")
    noop = facade.resume_run(ctx.session_id, run_id="run-completed", additional_steps=2)
    assert noop["status"] == "completed_noop"
    assert noop["reply"] is None

    mismatch = DiscussionGraphState.from_session(
        ctx, run_id="run-mismatch", max_steps=1, trace_id="trace-run-mismatch"
    )
    mismatch.run_status = "interrupted"
    mismatch.stop_reason = "max_steps_reached"
    mismatch.emitted_turn_ids = ["ally-999"]
    store.save(mismatch, status="interrupted")
    with pytest.raises(SessionNotFoundError):
        facade.resume_run(ctx.session_id, run_id="run-mismatch", additional_steps=1)


def test_quality_check_pass_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")
    ds = DiscussionService(cfg, ss)

    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.select_next_actor", lambda state, session: "ally")

    def _gen(state, session):
        session.turns.append(
            TranscriptTurn(
                turn_id=f"ally-{len(session.turns)+1}",
                speaker_role="ally",
                text="This is sufficiently detailed and clearly connected to the topic for passing quality checks.",
                created_at="2026-01-01T00:00:00Z",
            )
        )
        return session, AgentReply(role="ally", text=session.turns[-1].text)

    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.generate_turn", _gen)
    monkeypatch.setattr(
        "app.agent_runtime_v2.graphs.discussion_graph.quality_check",
        lambda state, session, reply, **kwargs: "pass",
    )
    sess, replies = ds.auto_run_discussion(ctx.session_id, max_steps=1, auto_fill_user=False)
    assert len(replies) == 1
    assert sess.turns[-1].metadata.get("quality_repaired") is None


def test_quality_repair_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")
    ds = DiscussionService(cfg, ss)
    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.select_next_actor", lambda state, session: "ally")

    def _gen(state, session):
        session.turns.append(
            TranscriptTurn(
                turn_id=f"ally-{len(session.turns)+1}",
                speaker_role="ally",
                text="short",
                created_at="2026-01-01T00:00:00Z",
            )
        )
        return session, AgentReply(role="ally", text="short")

    counter = {"n": 0}

    def _quality(state, session, reply, **kwargs):
        counter["n"] += 1
        return "repair" if counter["n"] == 1 else "pass"

    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.generate_turn", _gen)
    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.quality_check", _quality)
    sess, replies = ds.auto_run_discussion(ctx.session_id, max_steps=1, auto_fill_user=False)
    assert len(replies) == 1
    assert sess.turns[-1].metadata.get("quality_repaired") is True


def test_quality_interrupt_after_max_repairs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = _cfg(tmp_path)
    ss = SessionService(cfg)
    ctx = ss.manager.create_session(topic_id="tc-any", snapshot_dir=str(tmp_path), provider_name="mock")
    ds = DiscussionService(cfg, ss)
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
    sess, _replies = ds.auto_run_discussion(ctx.session_id, max_steps=2, auto_fill_user=False)
    assert len(sess.turns) == 0
    payload = FileCheckpointStore(cfg.agent_runtime_v2_dir / "checkpoints").load_latest_for_session(ctx.session_id)
    assert payload is not None
    state = payload.get("state") or {}
    assert state.get("stop_reason") == "interrupt_for_review"
    assert state.get("quality_decision") == "interrupt"
