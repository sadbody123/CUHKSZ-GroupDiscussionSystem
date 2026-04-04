"""Runtime demo CLI commands (no LLM)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.logging import setup_logging
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.evaluation.feedback_packet import build_feedback_packet
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.session.store import SessionStore
from app.runtime.snapshot_loader import load_snapshot


def _bundle(snapshot_dir: Path):
    setup_logging()
    return load_snapshot(snapshot_dir)


def list_topics(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
) -> None:
    """List topic cards with tags and approximate evidence hits."""
    b = _bundle(snapshot_dir)
    _ped, top, ev, _doc, _src = build_repositories(b)
    for c in top.list_topics():
        keys = {c.topic_id, *c.tags}
        seen: set[str] = set()
        for k in keys:
            for row in ev.by_topic(k):
                seen.add(row.evidence_id)
        typer.echo(f"{c.topic_id}\t{c.topic}\t{','.join(c.tags)}\tevidence_rows={len(seen)}")


def show_topic(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    topic_id: str = typer.Option(..., "--topic-id", "-t"),
) -> None:
    """Print one topic card as JSON."""
    b = _bundle(snapshot_dir)
    _ped, top, _ev, _doc, _src = build_repositories(b)
    card = top.get_topic(topic_id)
    if not card:
        typer.echo(f"topic_id not found: {topic_id}", err=True)
        raise typer.Exit(code=1)
    typer.echo(json.dumps(card.model_dump(), ensure_ascii=False, indent=2))


def retrieve_context(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    topic_id: Optional[str] = typer.Option(None, "--topic-id", "-t"),
    role: str = typer.Option("ally", "--role", "-r"),
    phase: str = typer.Option("discussion", "--phase", "-p"),
    top_k: int = typer.Option(5, "--top-k", "-k"),
) -> None:
    """Build RoleContextPacket JSON for a role (rule retrieval)."""
    b = _bundle(snapshot_dir)
    ped, top, ev, doc, _src = build_repositories(b)
    router = RoleRouter(ped, top, ev, doc)
    pkt = router.build_context_packet(role=role, topic_id=topic_id, session_phase=phase, top_k=top_k)
    typer.echo(json.dumps(pkt.model_dump(), ensure_ascii=False, indent=2))


def plan_turn(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    topic_id: Optional[str] = typer.Option(None, "--topic-id", "-t"),
    phase: str = typer.Option("discussion", "--phase", "-p"),
    last_role: Optional[str] = typer.Option(None, "--last-role"),
    transcript_file: Path = typer.Option(..., "--transcript-file", exists=True, dir_okay=False),
) -> None:
    """Produce TurnPlan with embedded context_packet (no natural language generation)."""
    b = _bundle(snapshot_dir)
    ped, top, ev, doc, _src = build_repositories(b)
    router = RoleRouter(ped, top, ev, doc)
    sm = SessionStateMachine(router)
    sid, tid, turns = SessionStore.load_transcript_file(transcript_file)
    tp = sm.build_turn_plan(
        session_id=sid,
        topic_id=topic_id or tid,
        phase=phase,
        last_role=last_role,
        transcript_turns=turns,
    )
    typer.echo(json.dumps(tp.model_dump(), ensure_ascii=False, indent=2))


def analyze_transcript_cmd(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    topic_id: Optional[str] = typer.Option(None, "--topic-id", "-t"),
    transcript_file: Path = typer.Option(..., "--transcript-file", exists=True, dir_okay=False),
) -> None:
    """Rule-based transcript metrics + FeedbackPacket JSON."""
    b = _bundle(snapshot_dir)
    ped, _top, _ev, _doc, _src = build_repositories(b)
    sid, tid, turns = SessionStore.load_transcript_file(transcript_file)
    metrics, sigs = analyze_transcript_turns(turns)
    fb = build_feedback_packet(
        session_id=str(sid),
        topic_id=topic_id or tid,
        metrics=metrics,
        detected_signals=sigs,
        pedagogy=ped,
    )
    typer.echo(json.dumps(fb.model_dump(), ensure_ascii=False, indent=2))


def register_runtime_cli(app: typer.Typer) -> None:
    """Register flat runtime commands on the root Typer app."""
    app.command("list-topics")(list_topics)
    app.command("show-topic")(show_topic)
    app.command("retrieve-context")(retrieve_context)
    app.command("plan-turn")(plan_turn)
    app.command("analyze-transcript")(analyze_transcript_cmd)
    from app.runtime.cli.discussion_commands import register_discussion_cli

    register_discussion_cli(app)
