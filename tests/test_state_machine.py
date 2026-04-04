"""Session phase machine tests (deterministic)."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2

from app.runtime.enums import RoleType, SessionPhase
from app.runtime.orchestrator import policies as pol
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn
from app.runtime.snapshot_loader import load_snapshot


def _turn(n: int, role: str, text: str = "ok") -> TranscriptTurn:
    return TranscriptTurn(turn_id=f"t{n}", speaker_role=role, text=text, created_at="")


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_prepare_to_intro_and_discussion(snapshot_v2_dir):
    b = load_snapshot(snapshot_v2_dir)
    ped, top, ev, doc, _ = build_repositories(b)
    sm = SessionStateMachine(RoleRouter(ped, top, ev, doc))

    ctx = SessionContext(session_id="s1", topic_id="tc-campus-ai", phase=SessionPhase.PREPARE.value, turns=[])
    assert sm.advance_phase(ctx) == SessionPhase.INTRO.value

    ctx.turns = [_turn(1, RoleType.USER.value)]
    assert sm.advance_phase(ctx) == SessionPhase.DISCUSSION.value


def test_discussion_to_summary_threshold():
    """Uses isolated SessionStateMachine with dummy router (not used in advance_phase)."""
    from app.runtime.repositories.pedagogy_repo import PedagogyRepository
    from app.runtime.repositories.topic_repo import TopicRepository
    from app.runtime.repositories.evidence_repo import EvidenceRepository
    from app.runtime.repositories.document_repo import DocumentRepository

    router = RoleRouter(
        PedagogyRepository([]),
        TopicRepository([]),
        EvidenceRepository([]),
        DocumentRepository([]),
    )
    sm = SessionStateMachine(router)

    turns = [_turn(i, RoleType.USER.value) for i in range(pol.DISCUSSION_MAX_TURNS)]
    ctx = SessionContext(
        session_id="s2",
        topic_id="x",
        phase=SessionPhase.DISCUSSION.value,
        turns=turns,
    )
    assert sm.advance_phase(ctx) == SessionPhase.SUMMARY.value


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_build_turn_plan_returns_packet(snapshot_v2_dir):
    b = load_snapshot(snapshot_v2_dir)
    ped, top, ev, doc, _ = build_repositories(b)
    sm = SessionStateMachine(RoleRouter(ped, top, ev, doc))
    turns = [
        TranscriptTurn.model_validate(x)
        for x in __import__("json").loads(
            (__import__("pathlib").Path(__file__).parent / "fixtures/runtime/sample_transcript.json").read_text(encoding="utf-8")
        )["turns"]
    ]
    tp = sm.build_turn_plan(
        session_id="sess",
        topic_id="tc-campus-ai",
        phase=SessionPhase.DISCUSSION.value,
        last_role="user",
        transcript_turns=turns,
    )
    assert tp.next_role
    assert tp.context_packet
