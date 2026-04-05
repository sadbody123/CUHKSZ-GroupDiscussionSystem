"""Validate local environment for running the stack."""

from __future__ import annotations

import importlib.util
import platform
from pathlib import Path
from typing import Any

from app.audio.analysis.providers.local_wave_analyzer import LocalWaveAnalyzer
from app.audio.providers.manager import get_asr_provider, get_tts_provider
from app.ops.settings import UnifiedSettings, get_ops_settings
from app.runtime.llm.manager import get_provider
from app.runtime.profile_loader import load_profile_yaml
from app.runtime.schemas.llm import GenerationRequest, LLMMessage


def _writable(d: Path) -> bool:
    try:
        d.mkdir(parents=True, exist_ok=True)
        p = d / ".write_test"
        p.write_text("ok", encoding="utf-8")
        p.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def validate_environment(settings: UnifiedSettings | None = None) -> dict[str, Any]:
    s = settings or get_ops_settings()
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    warnings.append(
        "paths_are_resolved: JSON uses absolute paths as returned by the OS "
        "(Windows drive letter casing may vary; separators follow the platform)."
    )
    if platform.system() == "Windows":
        warnings.append(
            "platform_windows: prefer forward slashes or quoted paths in PowerShell when setting "
            "SNAPSHOT_ROOT / SESSION_STORAGE_DIR in .env; verify paths after editing."
        )

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            errors.append(f"{name}: {detail}")

    # snapshot root (parent must exist; dir may be empty)
    snap = s.snapshot_root.resolve()
    add("snapshot_root_parent_exists", snap.parent.is_dir(), str(snap.parent))
    if snap.is_dir() and not any(snap.iterdir()):
        warnings.append("snapshot_root is empty")

    add("session_storage_writable", _writable(s.session_storage_dir), str(s.session_storage_dir))
    add("eval_report_dir_writable", _writable(s.eval_report_dir), str(s.eval_report_dir))
    add("feedback_report_dir_writable", _writable(s.feedback_report_dir), str(s.feedback_report_dir))
    add("bundle_dir_writable", _writable(s.bundle_dir), str(s.bundle_dir))
    add("audio_storage_writable", _writable(s.audio_storage_dir), str(s.audio_storage_dir))
    add("speech_report_dir_writable", _writable(s.speech_report_dir), str(s.speech_report_dir))
    add("learner_storage_writable", _writable(s.learner_storage_dir), str(s.learner_storage_dir))

    add("learner_analytics_flag", True, f"ENABLE_LEARNER_ANALYTICS={s.enable_learner_analytics}")
    hz = int(s.default_learning_plan_horizon)
    hz_ok = 2 <= hz <= 10
    add("learner_plan_horizon_sane", hz_ok, f"default_learning_plan_horizon={hz}")

    if s.auto_ingest_session_to_learner:
        w1 = _writable(s.session_storage_dir)
        w2 = _writable(s.learner_storage_dir)
        add(
            "auto_ingest_session_to_learner_writable",
            w1 and w2,
            "session + learner stores must be writable when AUTO_INGEST is on",
        )

    try:
        LocalWaveAnalyzer()
        add("local_wave_speech_analyzer", True, "local_wave")
    except Exception as e:
        add("local_wave_speech_analyzer", False, str(e))

    try:
        get_asr_provider("mock_asr", s)
        get_tts_provider("mock_tts", s)
        add("mock_audio_providers", True, "mock_asr/mock_tts")
    except Exception as e:
        add("mock_audio_providers", False, str(e))

    if s.default_asr_provider.lower() in ("openai_whisper", "openai-whisper", "whisper"):
        oa = bool(s.openai_api_key)
        add("openai_asr_configured", oa, "OPENAI_API_KEY required for OpenAI ASR" if not oa else "ok")
        if not oa:
            errors.append("openai_asr: missing API key")

    if s.default_tts_provider.lower() in ("openai_tts", "openai-tts"):
        oa = bool(s.openai_api_key)
        add("openai_tts_configured", oa, "OPENAI_API_KEY required for OpenAI TTS" if not oa else "ok")
        if not oa:
            errors.append("openai_tts: missing API key")

    prof_ok = True
    prof_detail = ""
    try:
        load_profile_yaml(s.default_runtime_profile)
    except Exception as e:
        prof_ok = False
        prof_detail = str(e)
    add("default_runtime_profile", prof_ok, prof_detail or s.default_runtime_profile)

    mock_ok = True
    mock_detail = ""
    try:
        p = get_provider("mock")
        req = GenerationRequest(
            provider_name="mock",
            messages=[LLMMessage(role="user", content="ping")],
            metadata={"role": "ally"},
        )
        r = p.generate(req)
        mock_ok = bool(r.text)
    except Exception as e:
        mock_ok = False
        mock_detail = str(e)
    add("mock_provider", mock_ok, mock_detail)

    if s.default_provider.lower() in ("openai", "openai_compatible", "openai-compatible"):
        oa_ok = bool(s.openai_api_key)
        add("openai_configured", oa_ok, "OPENAI_API_KEY missing" if not oa_ok else "ok")
        if not oa_ok:
            errors.append("openai: missing API key for configured provider")

    if getattr(s, "enable_practice_modes", True):
        try:
            from app.modes.config import get_modes_paths
            from app.modes.loaders.validators import default_mode_id
            from app.modes.loaders.yaml_loader import get_mode_registry

            mp = get_modes_paths()
            add("mode_asset_practice_modes_dir", mp.practice_modes_dir.is_dir(), str(mp.practice_modes_dir))
            add("mode_reports_writable", _writable(s.mode_reports_dir), str(s.mode_reports_dir))
            reg = get_mode_registry()
            dm = getattr(s, "default_mode_id", None) or default_mode_id()
            add("default_mode_id_resolvable", dm in reg.modes, dm)
            dt = getattr(s, "default_assessment_template_id", None) or "gd_assessment_4p_v1"
            add("default_assessment_template_resolvable", dt in reg.assessment_templates, dt)
        except Exception as e:
            add("practice_modes_bootstrap", False, str(e))

    if getattr(s, "enable_group_sim", True):
        try:
            from app.group_sim.config import roster_template_dir
            from app.group_sim.loaders.yaml_loader import get_roster_registry

            rdir = roster_template_dir()
            add("roster_template_dir_exists", rdir.is_dir(), str(rdir))
            add("group_reports_writable", _writable(s.group_reports_dir), str(s.group_reports_dir))
            reg = get_roster_registry()
            dr = getattr(s, "default_roster_template_id", None) or "gd_4p_balanced"
            add("default_roster_template_resolvable", dr in reg.all_templates(), dr)
        except Exception as e:
            add("group_sim_bootstrap", False, str(e))

    if getattr(s, "enable_curriculum_delivery", True):
        add("curriculum_custom_pack_writable", _writable(s.curriculum_custom_pack_dir), str(s.curriculum_custom_pack_dir))
        add("assignment_storage_writable", _writable(s.assignment_storage_dir), str(s.assignment_storage_dir))
        try:
            from app.curriculum.loaders.yaml_loader import load_builtin_pack

            dp = getattr(s, "default_curriculum_pack_id", "foundation_gd_pack")
            ok = load_builtin_pack(dp) is not None
            add("default_curriculum_pack_loadable", ok, dp)
        except Exception as e:
            add("default_curriculum_pack_loadable", False, str(e))
        if getattr(s, "enable_plan_to_pack_bridge", True) and getattr(s, "enable_learner_analytics", True):
            add("plan_to_pack_bridge_ok", True, "learner analytics available for bridge")

    if getattr(s, "active_release_profile", None) is not None:
        try:
            from app.release.loaders.profile_loader import load_release_profile

            load_release_profile(str(getattr(s, "active_release_profile", "v1_demo")))
            add("active_release_profile_loadable", True, str(getattr(s, "active_release_profile", "")))
        except Exception as e:
            add("active_release_profile_loadable", False, str(e))
        rr = getattr(s, "release_report_dir", None)
        if rr is not None:
            add("release_report_dir_writable", _writable(Path(rr)), str(rr))
        db = getattr(s, "demo_bundle_dir", None)
        if db is not None:
            add("demo_bundle_dir_writable", _writable(Path(db)), str(db))

    if getattr(s, "enable_final_delivery_ui", True):
        add("final_release_dir_writable", _writable(s.final_release_dir), str(s.final_release_dir))
        add("handover_manifest_dir_writable", _writable(s.release_manifest_dir), str(s.release_manifest_dir))
        add("bom_dir_writable", _writable(s.bom_dir), str(s.bom_dir))
        add("demo_kit_dir_writable", _writable(s.demo_kit_dir), str(s.demo_kit_dir))
        add("handover_kit_dir_writable", _writable(s.handover_kit_dir), str(s.handover_kit_dir))
        add("acceptance_evidence_dir_writable", _writable(s.acceptance_evidence_dir), str(s.acceptance_evidence_dir))
        add("final_docs_bundle_dir_writable", _writable(s.final_docs_bundle_dir), str(s.final_docs_bundle_dir))
        add("delivery_verification_dir_writable", _writable(s.delivery_verification_dir), str(s.delivery_verification_dir))

    if getattr(s, "enable_stability_audit", True):
        add("stability_report_dir_writable", _writable(s.stability_report_dir), str(s.stability_report_dir))
        add("consistency_report_dir_writable", _writable(s.consistency_report_dir), str(s.consistency_report_dir))
        add("e2e_results_dir_writable", _writable(s.e2e_results_dir), str(s.e2e_results_dir))
        add("known_issues_dir_writable", _writable(s.known_issues_dir), str(s.known_issues_dir))
        add("rc_report_dir_writable", _writable(s.rc_report_dir), str(s.rc_report_dir))

    if getattr(s, "enable_authoring_studio", True):
        ar = getattr(s, "authoring_root_dir", None)
        if ar is not None:
            add("authoring_root_writable", _writable(Path(ar)), str(ar))
            add(
                "authoring_subdirs_writable",
                _writable(Path(ar) / "drafts")
                and _writable(Path(ar) / "patches")
                and _writable(Path(ar) / "publications"),
                "drafts/patches/publications",
            )

    if getattr(s, "enable_review_workspace", True):
        add("review_storage_writable", _writable(s.review_storage_dir), str(s.review_storage_dir))
        add("reviewer_storage_writable", _writable(s.reviewer_storage_dir), str(s.reviewer_storage_dir))
        rub = getattr(s, "default_review_rubric_id", None)
        if rub:
            add("default_review_rubric_id_set", True, str(rub))
        if getattr(s, "enable_override_merge", True):
            add(
                "override_merge_review_outputs_writable",
                _writable(s.review_storage_dir / "reviewed_outputs"),
                str(s.review_storage_dir / "reviewed_outputs"),
            )

    for mod in ("fastapi", "uvicorn", "httpx", "streamlit"):
        spec = importlib.util.find_spec(mod)
        ok = spec is not None
        checks.append({"name": f"import_{mod}", "ok": ok, "detail": mod if ok else "not installed"})
        if not ok:
            warnings.append(f"optional dependency not installed: {mod}")

    overall = "ok" if not errors else "error"
    return {
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "overall_status": overall,
        "platform": platform.system(),
        "path_style_note": "All directory checks use pathlib resolved paths for consistency across OS.",
    }
