"""CLI commands for audio MVP (registered on root Typer app)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.application.session_service import SessionService
from app.application.audio_service import AudioService
from app.application.speech_analysis_service import SpeechAnalysisService
from app.logging import setup_logging


def _app_config(storage_root: Optional[Path]) -> AppConfig:
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
    return cfg


def _session_service(storage_root: Optional[Path]) -> tuple[AppConfig, SessionService]:
    cfg = _app_config(storage_root)
    return cfg, SessionService(cfg)


def transcribe_audio_cmd(
    audio_file: Path = typer.Option(..., "--audio-file", exists=True, dir_okay=False),
    provider: str = typer.Option("mock_asr", "--provider"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
    save_asset: bool = typer.Option(False, "--save-asset"),
    session_id: Optional[str] = typer.Option(None, "--session-id", help="Required if --save-asset"),
) -> None:
    """Transcribe a WAV (or raw) file using ASR (default: mock)."""
    setup_logging()
    cfg, ss = _session_service(storage_root)
    audio = AudioService(cfg, ss)
    if save_asset and not session_id:
        typer.echo("--session-id required when using --save-asset", err=True)
        raise typer.Exit(1)
    resp, rec = audio.transcribe_audio_file(
        session_id=session_id,
        audio_path=audio_file,
        provider_name=provider,
        save_asset=save_asset,
    )
    out: dict = {"transcript": resp.text, "provider": resp.provider_name}
    if rec:
        out["asset"] = rec.model_dump()
    typer.echo(json.dumps(out, ensure_ascii=False, indent=2))


def submit_user_audio_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    audio_file: Path = typer.Option(..., "--audio-file", exists=True, dir_okay=False),
    provider: str = typer.Option("mock_asr", "--provider"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Submit audio as a user turn (ASR + session write)."""
    setup_logging()
    cfg, ss = _session_service(storage_root)
    audio = AudioService(cfg, ss)
    try:
        out = audio.submit_user_audio_turn(session_id, audio_file, provider_name=provider)
    except Exception as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from e
    typer.echo(json.dumps(out, ensure_ascii=False, indent=2, default=str))


def synthesize_turn_audio_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    turn_id: str = typer.Option(..., "--turn-id"),
    provider: str = typer.Option("mock_tts", "--provider"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    """Synthesize speech for one transcript turn."""
    setup_logging()
    cfg, ss = _session_service(storage_root)
    audio = AudioService(cfg, ss)
    try:
        rec = audio.synthesize_turn_audio(session_id, turn_id, provider_name=provider)
    except Exception as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from e
    typer.echo(json.dumps(rec.model_dump(), ensure_ascii=False, indent=2, default=str))


def list_audio_assets_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    setup_logging()
    cfg, ss = _session_service(storage_root)
    audio = AudioService(cfg, ss)
    rows = audio.list_session_audio_assets(session_id)
    typer.echo(json.dumps([r.model_dump() for r in rows], ensure_ascii=False, indent=2))


def export_audio_asset_cmd(
    asset_id: str = typer.Option(..., "--asset-id"),
    output_file: Path = typer.Option(..., "--output-file", "-o"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    setup_logging()
    cfg, ss = _session_service(storage_root)
    audio = AudioService(cfg, ss)
    try:
        rec = audio.export_audio_asset_to_path(asset_id, output_file)
    except Exception as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from e
    typer.echo(json.dumps({"ok": True, "asset_id": rec.asset_id, "output": str(output_file.resolve())}, indent=2))


def analyze_turn_audio_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    turn_id: str = typer.Option(..., "--turn-id"),
    profile_id: str = typer.Option("speech_default", "--profile-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    setup_logging()
    cfg, ss = _session_service(storage_root)
    sas = SpeechAnalysisService(cfg, ss)
    try:
        out = sas.analyze_turn_audio(session_id, turn_id, profile_id=profile_id)
    except Exception as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from e
    typer.echo(json.dumps(out, ensure_ascii=False, indent=2, default=str))


def analyze_session_speech_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    profile_id: str = typer.Option("speech_default", "--profile-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    setup_logging()
    cfg, ss = _session_service(storage_root)
    sas = SpeechAnalysisService(cfg, ss)
    try:
        out = sas.analyze_session_speech(session_id, profile_id=profile_id)
    except Exception as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from e
    typer.echo(json.dumps(out, ensure_ascii=False, indent=2, default=str))


def show_speech_report_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    setup_logging()
    cfg, ss = _session_service(storage_root)
    sas = SpeechAnalysisService(cfg, ss)
    r = sas.get_session_speech_report(session_id)
    typer.echo(json.dumps(r or {}, ensure_ascii=False, indent=2, default=str))


def export_speech_report_cmd(
    session_id: str = typer.Option(..., "--session-id"),
    output_file: Path = typer.Option(..., "--output-file", "-o"),
    storage_root: Optional[Path] = typer.Option(None, "--storage-root", dir_okay=True),
) -> None:
    setup_logging()
    cfg, ss = _session_service(storage_root)
    sas = SpeechAnalysisService(cfg, ss)
    r = sas.get_session_speech_report(session_id)
    if not r:
        typer.echo("no speech report", err=True)
        raise typer.Exit(1)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(str(output_file.resolve()))


def register_audio_cli(app: typer.Typer) -> None:
    app.command("transcribe-audio")(transcribe_audio_cmd)
    app.command("submit-user-audio")(submit_user_audio_cmd)
    app.command("synthesize-turn-audio")(synthesize_turn_audio_cmd)
    app.command("list-audio-assets")(list_audio_assets_cmd)
    app.command("export-audio-asset")(export_audio_asset_cmd)
    app.command("analyze-turn-audio")(analyze_turn_audio_cmd)
    app.command("analyze-session-speech")(analyze_session_speech_cmd)
    app.command("show-speech-report")(show_speech_report_cmd)
    app.command("export-speech-report")(export_speech_report_cmd)
