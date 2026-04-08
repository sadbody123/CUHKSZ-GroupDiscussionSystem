"""API tests for runtime review endpoints."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_config
from app.api.main import create_app
from app.application.config import get_app_config
from app.application.discussion_service import DiscussionService
from app.application.session_service import SessionService
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.transcript import TranscriptTurn


def test_runtime_review_api_basic_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("langgraph")
    cfg = get_app_config().model_copy(
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
    sessions = SessionService(cfg)
    disc = DiscussionService(cfg, sessions)
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

    app = create_app()
    app.dependency_overrides[get_config] = lambda: cfg
    with TestClient(app) as client:
        r = client.get("/runtime-reviews")
        assert r.status_code == 200
        rows = r.json()
        assert rows
        rid = rows[0]["review_id"]
        d = client.get(f"/runtime-reviews/{rid}")
        assert d.status_code == 200
        p = d.json()
        assert p["status"] == "pending"
        a = client.post(
            f"/runtime-reviews/{rid}/apply-edited-draft",
            json={
                "edited_text": "Manually corrected response with stronger relevance.",
                "expected_version": p["version"],
                "updated_by": "teacher_api",
            },
        )
        assert a.status_code == 200
        m = client.get("/runtime-reviews/metrics/summary")
        assert m.status_code == 200
        ev = client.get(f"/sessions/{ctx.session_id}/runtime-events", params={"limit": 20})
        assert ev.status_code == 200
        ev_body = ev.json()
        assert ev_body["session_id"] == ctx.session_id
        assert isinstance(ev_body["items"], list)
        if rows and rows[0].get("run_id"):
            ev_run = client.get(
                f"/sessions/{ctx.session_id}/runtime-events",
                params={"limit": 20, "run_id": rows[0]["run_id"]},
            )
            assert ev_run.status_code == 200


def test_runtime_review_api_supports_session_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("langgraph")
    cfg = get_app_config().model_copy(
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
    sessions = SessionService(cfg)
    disc = DiscussionService(cfg, sessions)
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

    app = create_app()
    app.dependency_overrides[get_config] = lambda: cfg
    with TestClient(app) as client:
        ok = client.get(f"/runtime-reviews?status=pending&session_id={ctx.session_id}")
        assert ok.status_code == 200
        rows = ok.json()
        assert rows
        assert all(r["session_id"] == ctx.session_id for r in rows)
