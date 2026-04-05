"""CLI for text discussion MVP (phase 4)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.session_service import SessionService
from app.logging import setup_logging
from app.runtime.execution.discussion_loop import auto_run_discussion
from app.runtime.execution.feedback_runner import run_generate_feedback
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.session.manager import SessionManager
from app.runtime.session.file_store import FileSessionStore


def _manager(store_root: Optional[Path] = None) -> SessionManager:
    setup_logging()
    return SessionManager(FileSessionStore(store_root))


def _discussion_stack(storage_root: Optional[Path] = None) -> tuple[DiscussionService, FeedbackService]:
    setup_logging()
    cfg = AppConfig.from_env()
    if storage_root is not None:
        r = storage_root.resolve()
        cfg = cfg.model_copy(
            update={
                "session_storage_dir": r,
                "audio_storage_dir": r.parent / "audio",
                "speech_report_dir": r.parent / "speech_reports",
            }
        )
    ss = SessionService(cfg)
    return DiscussionService(cfg, ss), FeedbackService(ss)


def create_session_cmd(
    snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    topic_id: str = typer.Option(..., "--topic-id", "-t"),
    user_stance: Optional[str] = typer.Option(None, "--user-stance"),
    provider: str = typer.Option("mock", "--provider", "-p"),
    model: Optional[str] = typer.Option(None, "--model"),
    runtime_profile: str = typer.Option("default", "--runtime-profile"),
    learner_id: Optional[str] = typer.Option(None, "--learner-id"),
    mode_id: Optional[str] = typer.Option(None, "--mode-id"),
    preset_id: Optional[str] = typer.Option(None, "--preset-id"),
    drill_id: Optional[str] = typer.Option(None, "--drill-id"),
    assessment_template_id: Optional[str] = typer.Option(None, "--assessment-template-id"),
    roster_template_id: Optional[str] = typer.Option(None, "--roster-template-id"),
    user_participant_id: Optional[str] = typer.Option(None, "--user-participant-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Create a new discussion session and persist it."""
    cfg = AppConfig.from_env()
    if storage_root is not None:
        r = storage_root.resolve()
        cfg = cfg.model_copy(
            update={
                "session_storage_dir": r,
                "audio_storage_dir": r.parent / "audio",
                "speech_report_dir": r.parent / "speech_reports",
                "mode_reports_dir": r.parent / "mode_reports",
                "group_reports_dir": r.parent / "group_reports",
            }
        )
    ss = SessionService(cfg)
    snapshot_id = snapshot_dir.name
    ctx = ss.create_session(
        snapshot_id=snapshot_id,
        topic_id=topic_id,
        user_stance=user_stance,
        provider_name=provider,
        model_name=model,
        runtime_profile_id=runtime_profile,
        learner_id=learner_id,
        mode_id=mode_id,
        preset_id=preset_id,
        drill_id=drill_id,
        assessment_template_id=assessment_template_id,
        roster_template_id=roster_template_id,
        user_participant_id=user_participant_id,
        source="cli",
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
    with_tts: bool = typer.Option(False, "--with-tts"),
    tts_provider: Optional[str] = typer.Option(None, "--tts-provider"),
) -> None:
    """Run next non-user role (mock or configured LLM)."""
    use_audio = with_tts or bool(tts_provider)
    if use_audio:
        disc, _fb = _discussion_stack(storage_root)
        sess, reply, next_role = disc.run_next_turn(
            session_id, with_tts=True, tts_provider=tts_provider
        )
        payload = {
            "next_role": next_role,
            "reply": reply.model_dump() if reply else None,
            "turn_count": len(sess.turns),
        }
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
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
    with_tts: bool = typer.Option(False, "--with-tts"),
    tts_provider: Optional[str] = typer.Option(None, "--tts-provider"),
    with_speech_analysis: bool = typer.Option(False, "--with-speech-analysis"),
    speech_profile_id: Optional[str] = typer.Option(None, "--speech-profile-id"),
) -> None:
    """Build FeedbackPacket + CoachReport."""
    use_audio = with_tts or bool(tts_provider)
    if use_audio or with_speech_analysis:
        _disc, fb = _discussion_stack(storage_root)
        report = fb.generate_feedback(
            session_id,
            with_tts=use_audio,
            tts_provider=tts_provider,
            with_speech_analysis=with_speech_analysis,
            speech_profile_id=speech_profile_id,
        )
        typer.echo(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))
        return
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
