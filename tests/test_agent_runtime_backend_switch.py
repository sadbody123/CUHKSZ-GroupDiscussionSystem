"""V1/V2 runtime backend switch tests."""

from __future__ import annotations

import pytest

from app.agent_runtime_v2.facade.runtime_factory import resolve_runtime_backend
from app.application.config import AppConfig
from app.application.discussion_service import DiscussionService
from app.application.session_service import SessionService
from app.ops.settings import get_ops_settings


def test_backend_default_is_v1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENT_RUNTIME_BACKEND", raising=False)
    get_ops_settings.cache_clear()
    cfg = AppConfig.from_env()
    assert cfg.agent_runtime_backend == "v1"
    assert resolve_runtime_backend(cfg) == "v1"


def test_backend_can_switch_to_v2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_RUNTIME_BACKEND", "v2")
    get_ops_settings.cache_clear()
    cfg = AppConfig.from_env()
    assert cfg.agent_runtime_backend == "v2"
    assert resolve_runtime_backend(cfg) == "v2"


def test_backend_invalid_value_falls_back_to_v1() -> None:
    cfg = AppConfig.from_env().model_copy(update={"agent_runtime_backend": "legacy"})
    assert resolve_runtime_backend(cfg) == "v1"


def test_discussion_service_runtime_selection(tmp_path) -> None:
    base = AppConfig.from_env().model_copy(
        update={
            "session_storage_dir": tmp_path / "sessions",
            "audio_storage_dir": tmp_path / "audio",
            "speech_report_dir": tmp_path / "speech_reports",
            "mode_reports_dir": tmp_path / "mode_reports",
            "group_reports_dir": tmp_path / "group_reports",
        }
    )
    service_v1 = DiscussionService(base.model_copy(update={"agent_runtime_backend": "v1"}), SessionService(base))
    assert service_v1._v2_runtime is None  # type: ignore[attr-defined]
    service_v2 = DiscussionService(base.model_copy(update={"agent_runtime_backend": "v2"}), SessionService(base))
    assert service_v2._v2_runtime is not None  # type: ignore[attr-defined]


def test_v1_backend_does_not_require_langgraph(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("app.agent_runtime_v2.graphs.discussion_graph.has_langgraph_support", lambda: False)
    cfg = AppConfig.from_env().model_copy(
        update={
            "agent_runtime_backend": "v1",
            "session_storage_dir": tmp_path / "sessions",
            "audio_storage_dir": tmp_path / "audio",
            "speech_report_dir": tmp_path / "speech_reports",
            "mode_reports_dir": tmp_path / "mode_reports",
            "group_reports_dir": tmp_path / "group_reports",
        }
    )
    service = DiscussionService(cfg, SessionService(cfg))
    assert service._v2_runtime is None  # type: ignore[attr-defined]
