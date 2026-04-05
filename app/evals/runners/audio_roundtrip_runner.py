"""audio_roundtrip_case — mock ASR/TTS + session + assets."""

from __future__ import annotations

from pathlib import Path

from app.application.audio_service import AudioService
from app.application.config import get_app_config
from app.application.discussion_service import DiscussionService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_audio_roundtrip_case(case: EvalCase, snapshot_dir: Path, profile_id: str, tmp_root: Path) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    sess_root = tmp_root / "sessions"
    audio_root = tmp_root / "audio"
    sess_root.mkdir(parents=True, exist_ok=True)
    audio_root.mkdir(parents=True, exist_ok=True)
    cfg = get_app_config().model_copy(
        update={
            "session_storage_dir": sess_root.resolve(),
            "audio_storage_dir": audio_root.resolve(),
        }
    )
    project_root = Path(__file__).resolve().parents[3]
    wav_rel = Path(str(inp["audio_file"]))
    wav = wav_rel if wav_rel.is_absolute() else (project_root / wav_rel).resolve()

    snap_name = snapshot_dir.name
    svc = SessionService(cfg)
    disc = DiscussionService(cfg, svc)
    ctx = svc.create_session(
        snapshot_id=snap_name,
        topic_id=str(inp["topic_id"]),
        user_stance=inp.get("user_stance"),
        provider_name=str(inp.get("provider_name", "mock")),
        runtime_profile_id=profile_id or case.runtime_profile_id or "default",
        source="eval_audio",
    )
    audio = AudioService(cfg, svc)
    audio.submit_user_audio_turn(
        ctx.session_id,
        wav,
        provider_name=str(inp.get("provider_name_asr", "mock_asr")),
    )
    disc.run_next_turn(
        ctx.session_id,
        with_tts=True,
        tts_provider=str(inp.get("provider_name_tts", "mock_tts")),
    )
    sess = svc.get_session(ctx.session_id)
    assets = audio.list_session_audio_assets(ctx.session_id)
    ok = True
    if exp.get("min_audio_asset_count") is not None:
        ok = ok and len(assets) >= int(exp["min_audio_asset_count"])
    if exp.get("created_turn_input_mode"):
        want = str(exp["created_turn_input_mode"])
        ut = next((t for t in sess.turns if t.speaker_role.lower() == "user"), None)
        ok = ok and ut is not None and ut.input_mode == want
    if exp.get("transcript_contains_any"):
        ut = next((t for t in sess.turns if t.speaker_role.lower() == "user"), None)
        txt = (ut.text if ut else "").lower()
        ok = ok and any(str(s).lower() in txt for s in exp["transcript_contains_any"])
    if exp.get("tts_asset_created"):
        last_ai = next((t for t in reversed(sess.turns) if t.speaker_role.lower() != "user"), None)
        ok = ok and last_ai is not None and bool(last_ai.tts_asset_id)
    if exp.get("mime_type"):
        want_m = str(exp["mime_type"])
        ok = ok and any(a.mime_type == want_m for a in assets)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"assets": len(assets), "turns": len(sess.turns)},
        metadata={"session_id": ctx.session_id},
    )
