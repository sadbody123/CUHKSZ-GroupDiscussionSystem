"""speech_delivery_case — proxy metrics + disclaimer regression."""

from __future__ import annotations

from pathlib import Path

from app.application.config import get_app_config
from app.application.session_service import SessionService
from app.application.speech_analysis_service import SpeechAnalysisService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_speech_delivery_case(case: EvalCase, snapshot_dir: Path, profile_id: str, tmp_root: Path) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    sess_root = tmp_root / "sessions"
    audio_root = tmp_root / "audio"
    speech_root = tmp_root / "speech_reports"
    for d in (sess_root, audio_root, speech_root):
        d.mkdir(parents=True, exist_ok=True)
    cfg = get_app_config().model_copy(
        update={
            "session_storage_dir": sess_root.resolve(),
            "audio_storage_dir": audio_root.resolve(),
            "speech_report_dir": speech_root.resolve(),
        }
    )
    project_root = Path(__file__).resolve().parents[3]
    wav_rel = Path(str(inp["audio_file"]))
    wav = wav_rel if wav_rel.is_absolute() else (project_root / wav_rel).resolve()

    from app.application.audio_service import AudioService

    snap_name = snapshot_dir.name
    svc = SessionService(cfg)
    audio = AudioService(cfg, svc)
    sas = SpeechAnalysisService(cfg, svc)
    pid = profile_id or inp.get("profile_id") or "speech_default"
    ctx = svc.create_session(
        snapshot_id=snap_name,
        topic_id=str(inp["topic_id"]),
        user_stance=inp.get("user_stance"),
        provider_name=str(inp.get("provider_name", "mock")),
        runtime_profile_id=pid,
        source="eval_speech",
    )
    audio.submit_user_audio_turn(ctx.session_id, wav, provider_name="mock_asr")
    rep = sas.analyze_session_speech(ctx.session_id, profile_id=pid)
    ok = True
    if exp.get("require_proxy_disclaimer"):
        ok = ok and bool(rep.get("proxy_disclaimer"))
    if exp.get("min_aggregate_turns") is not None:
        ok = ok and int((rep.get("aggregate_metrics") or {}).get("turns_analyzed", 0)) >= int(
            exp["min_aggregate_turns"]
        )
    if exp.get("required_signal_types"):
        sigs = rep.get("signals") or []
        types = {str(s.get("signal_type")) for s in sigs}
        for t in exp["required_signal_types"]:
            ok = ok and t in types
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"report_id": rep.get("report_id")},
        metadata={"session_id": ctx.session_id},
    )
