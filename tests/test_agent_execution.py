"""Agent execution with mock provider."""

from __future__ import annotations

import pytest

from app.runtime.agents.base import run_agent_turn
from app.runtime.llm.manager import get_provider
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.session import SessionContext
from app.runtime.snapshot_loader import load_snapshot
from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_agents_run(snapshot_v2_dir):
    b = load_snapshot(snapshot_v2_dir)
    ped, top, ev, doc, _ = build_repositories(b)
    router = RoleRouter(ped, top, ev, doc)
    prov = get_provider("mock")
    session = SessionContext(
        session_id="s",
        topic_id="tc-campus-ai",
        phase="discussion",
        provider_name="mock",
        snapshot_dir=str(snapshot_v2_dir),
    )
    for role in ("moderator", "ally", "opponent"):
        r = run_agent_turn(router=router, provider=prov, role=role, session=session)
        assert r.text
        assert r.used_pedagogy_item_ids is not None
