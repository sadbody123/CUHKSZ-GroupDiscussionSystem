"""CLI for text discussion MVP (phase 4)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.logging import setup_logging
from app.runtime.execution.discussion_loop import auto_run_discussion
from app.runtime.execution.feedback_runner import run_generate_feedback
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.session.manager import SessionManager
from app.runtime.session.file_store import FileSessionStore


def _manager(store_root: Optional[Path] = None) -> SessionManager:
    setup_logging()
    return SessionManager(FileSessionStore(store_root))


def create_session_cmd(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    topic_id: str = typer.Option(..., "--topic-id", "-t"),
    user_stance: Optional[str] = typer.Option(None, "--user-stance"),
    provider: str = typer.Option("mock", "--provider", "-p"),
    model: Optional[str] = typer.Option(None, "--model"),
    runtime_profile: str = typer.Option("default", "--runtime-profile"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Create a new discussion session and persist it."""
    mgr = _manager(storage_root)
    ctx = mgr.create_session(
        topic_id=topic_id,
        snapshot_dir=str(snapshot_dir.resolve()),
        user_stance=user_stance,
        provider_name=provider,
        model_name=model,
        runtime_profile_id=runtime_profile,
    )
    typer.echo(ctx.session_id)


def session_status(
    session_id: str = typer.Option(..., "--session-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Show session phase, turn counts, recent transcript."""
    mgr = _manager(storage_root)
    ctx = mgr.load(session_id)
    if not ctx:
        typer.echo("session not found", err=True)
        raise typer.Exit(1)
    payload = {
        "session_id": ctx.session_id,
        "phase": ctx.phase,
        "topic_id": ctx.topic_id,
        "turns": len(ctx.turns),
        "provider": ctx.provider_name,
        "recent": [t.model_dump() for t in ctx.turns[-5:]],
        "can_run_next": True,
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def submit_user_turn(
    session_id: str = typer.Option(..., "--session-id"),
    text: str = typer.Option(..., "--text"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Append a user turn."""
    mgr = _manager(storage_root)
    ctx = mgr.load(session_id)
    if not ctx or not ctx.snapshot_dir:
        typer.echo("session not found", err=True)
        raise typer.Exit(1)
    ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
    ex.submit_user_turn(text)
    mgr.save(ex.session)
    typer.echo(json.dumps({"ok": True, "turns": len(ex.session.turns)}, ensure_ascii=False))


def run_next_turn(
    session_id: str = typer.Option(..., "--session-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Run next non-user role (mock or configured LLM)."""
    mgr = _manager(storage_root)
    ctx = mgr.load(session_id)
    if not ctx or not ctx.snapshot_dir:
        typer.echo("session not found", err=True)
        raise typer.Exit(1)
    ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
    sess, reply = ex.run_next_turn()
    mgr.save(sess)
    if reply is None:
        typer.echo(json.dumps({"next_role": "user", "message": "Your turn — submit-user-turn"}, ensure_ascii=False))
        return
    typer.echo(json.dumps({"reply": reply.model_dump()}, ensure_ascii=False, indent=2))


def auto_run_discussion_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    max_steps: int = typer.Option(4, "--max-steps"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Auto-advance with stub user lines between agent turns."""
    mgr = _manager(storage_root)
    ctx = mgr.load(session_id)
    if not ctx or not ctx.snapshot_dir:
        typer.echo("session not found", err=True)
        raise typer.Exit(1)
    ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
    sess, replies = auto_run_discussion(ex, max_steps=max_steps, auto_fill_user=True)
    mgr.save(sess)
    typer.echo(json.dumps({"replies": [r.model_dump() for r in replies]}, ensure_ascii=False, indent=2))


def generate_feedback_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Build FeedbackPacket + CoachReport."""
    mgr = _manager(storage_root)
    ctx = mgr.load(session_id)
    if not ctx or not ctx.snapshot_dir:
        typer.echo("session not found", err=True)
        raise typer.Exit(1)
    ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
    report = run_generate_feedback(ex, mgr)
    typer.echo(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))


def export_session(
    session_id: str = typer.Option(..., "--session-id"),
    output_file: Path = typer.Option(..., "--output-file", "-o"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Export full session JSON."""
    mgr = _manager(storage_root)
    ctx = mgr.load(session_id)
    if not ctx:
        typer.echo("session not found", err=True)
        raise typer.Exit(1)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(ctx.model_dump_json(indent=2) + "\n", encoding="utf-8")
    typer.echo(str(output_file.resolve()))


def register_discussion_cli(app: typer.Typer) -> None:
    app.command("create-session")(create_session_cmd)
    app.command("session-status")(session_status)
    app.command("submit-user-turn")(submit_user_turn)
    app.command("run-next-turn")(run_next_turn)
    app.command("auto-run-discussion")(auto_run_discussion_cmd)
    app.command("generate-feedback")(generate_feedback_cmd)
    app.command("export-session")(export_session)
