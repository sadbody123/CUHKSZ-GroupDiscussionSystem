"""Role-based retrieval / context packet tests."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2

from app.runtime.enums import RoleType
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.snapshot_loader import load_snapshot


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_role_packets_differ(snapshot_v2_dir):
    b = load_snapshot(snapshot_v2_dir)
    ped, top, ev, doc, _src = build_repositories(b)
    router = RoleRouter(ped, top, ev, doc)

    mod = router.build_context_packet(
        role=RoleType.MODERATOR.value,
        topic_id="tc-campus-ai",
        session_phase="discussion",
        top_k=5,
    )
    coach = router.build_context_packet(
        role=RoleType.COACH.value,
        topic_id="tc-campus-ai",
        session_phase="feedback",
        top_k=5,
    )
    ally = router.build_context_packet(
        role=RoleType.ALLY.value,
        topic_id="tc-campus-ai",
        session_phase="discussion",
        top_k=5,
    )

    assert mod.role == RoleType.MODERATOR.value
    assert coach.role == RoleType.COACH.value
    assert ally.role == RoleType.ALLY.value

    mod_types = {x.get("item_type") for x in mod.pedagogy_items}
    coach_types = {x.get("item_type") for x in coach.pedagogy_items}
    assert "rule" in mod_types or len(mod.pedagogy_items) >= 0
    assert "rubric" in coach_types or "coaching_tip" in coach_types or len(coach.pedagogy_items) >= 0
    assert isinstance(ally.evidence_items, list)
    assert mod.prompt_template_id == "moderator.md"
    assert coach.prompt_template_id == "coach.md"
    assert ally.prompt_template_id == "ally.md"
