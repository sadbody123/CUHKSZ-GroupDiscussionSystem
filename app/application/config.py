"""Application-layer configuration (API / UI / services)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from app.ops.settings import get_ops_settings


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_curriculum_builtin_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "curriculum" / "packs"


class AppConfig(BaseModel):
    """Settings for service layer, distinct from offline build `Settings`."""

    project_root: Path = Field(default_factory=_project_root)
    snapshot_root: Path
    session_storage_dir: Path
    default_provider: str = "mock"
    default_model: str | None = None
    default_runtime_profile: str = "default"
    agent_runtime_backend: str = "v1"
    agent_runtime_v2_dir: Path
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    ui_api_base_url: str = "http://127.0.0.1:8000"
    audio_storage_dir: Path
    enable_audio: bool = True
    default_asr_provider: str = "mock_asr"
    default_tts_provider: str = "mock_tts"
    max_audio_upload_mb: int = 25
    speech_report_dir: Path
    enable_speech_analysis: bool = True
    default_speech_analyzer: str = "local_wave"
    learner_storage_dir: Path
    enable_learner_analytics: bool = True
    default_learning_plan_horizon: int = 4
    learner_recommendation_max_items: int = 12
    learner_recent_window: int = 3
    learner_baseline_window: int = 3
    auto_ingest_session_to_learner: bool = False
    enable_learner_ui_panels: bool = True
    enable_practice_modes: bool = True
    mode_reports_dir: Path
    default_mode_id: str = "free_practice"
    default_preset_id: str = "free_practice"
    default_assessment_template_id: str = "gd_assessment_4p_v1"
    enable_prep_phase: bool = True
    enable_assessment_timer: bool = True
    micro_drill_max_steps: int = 12
    auto_generate_mode_report: bool = True
    enable_group_sim: bool = True
    group_reports_dir: Path
    default_roster_template_id: str = "gd_4p_balanced"
    default_4p_roster_template_id: str = "gd_4p_balanced"
    default_6p_roster_template_id: str = "gd_6p_balanced"
    enable_balance_warnings: bool = True
    max_same_participant_consecutive_turns: int = 2
    max_same_team_consecutive_turns: int = 2
    auto_generate_group_report: bool = True
    enable_review_workspace: bool = True
    review_storage_dir: Path
    reviewer_storage_dir: Path
    auto_create_review_pack_after_feedback: bool = False
    default_review_rubric_id: str | None = None
    review_queue_max_items: int = 500
    enable_override_merge: bool = True
    calibration_delta_warn_threshold: float = 0.35
    enable_curriculum_delivery: bool = True
    curriculum_pack_builtin_dir: Path
    curriculum_custom_pack_dir: Path
    assignment_storage_dir: Path
    default_curriculum_pack_id: str = "foundation_gd_pack"
    default_assignment_completion_policy: str = "min_one_step"
    auto_attach_session_to_assignment: bool = False
    auto_generate_assignment_report: bool = False
    enable_plan_to_pack_bridge: bool = True
    enable_authoring_studio: bool = True
    authoring_root_dir: Path
    authoring_published_runtime_profile_dir: Path
    authoring_published_misc_dir: Path
    default_author_id: str = "author_local"
    enable_authoring_preview: bool = True
    require_validation_before_publish: bool = True
    require_preview_before_publish: bool = False
    authoring_max_preview_steps: int = 50
    authoring_allow_derivative_from_builtin: bool = True
    active_release_profile: str = "v1_demo"

    @classmethod
    def from_env(cls) -> AppConfig:
        o = get_ops_settings()
        builtin = o.curriculum_pack_builtin_dir.resolve() if o.curriculum_pack_builtin_dir else _default_curriculum_builtin_dir().resolve()
        ar = o.authoring_root_dir.resolve()
        return cls(
            project_root=o.project_root.resolve(),
            snapshot_root=o.snapshot_root.resolve(),
            session_storage_dir=o.session_storage_dir.resolve(),
            default_provider=o.default_provider,
            default_model=o.default_model,
            default_runtime_profile=o.default_runtime_profile,
            agent_runtime_backend=o.agent_runtime_backend,
            agent_runtime_v2_dir=o.agent_runtime_v2_dir.resolve(),
            api_host=o.api_host,
            api_port=o.api_port,
            ui_api_base_url=o.ui_api_base_url,
            audio_storage_dir=o.audio_storage_dir.resolve(),
            enable_audio=o.enable_audio,
            default_asr_provider=o.default_asr_provider,
            default_tts_provider=o.default_tts_provider,
            max_audio_upload_mb=o.max_audio_upload_mb,
            speech_report_dir=o.speech_report_dir.resolve(),
            enable_speech_analysis=o.enable_speech_analysis,
            default_speech_analyzer=o.default_speech_analyzer,
            learner_storage_dir=o.learner_storage_dir.resolve(),
            enable_learner_analytics=o.enable_learner_analytics,
            default_learning_plan_horizon=o.default_learning_plan_horizon,
            learner_recommendation_max_items=o.learner_recommendation_max_items,
            learner_recent_window=o.learner_recent_window,
            learner_baseline_window=o.learner_baseline_window,
            auto_ingest_session_to_learner=o.auto_ingest_session_to_learner,
            enable_learner_ui_panels=o.enable_learner_ui_panels,
            enable_practice_modes=o.enable_practice_modes,
            mode_reports_dir=o.mode_reports_dir.resolve(),
            default_mode_id=o.default_mode_id,
            default_preset_id=o.default_preset_id,
            default_assessment_template_id=o.default_assessment_template_id,
            enable_prep_phase=o.enable_prep_phase,
            enable_assessment_timer=o.enable_assessment_timer,
            micro_drill_max_steps=o.micro_drill_max_steps,
            auto_generate_mode_report=o.auto_generate_mode_report,
            enable_group_sim=o.enable_group_sim,
            group_reports_dir=o.group_reports_dir.resolve(),
            default_roster_template_id=o.default_roster_template_id,
            default_4p_roster_template_id=o.default_4p_roster_template_id,
            default_6p_roster_template_id=o.default_6p_roster_template_id,
            enable_balance_warnings=o.enable_balance_warnings,
            max_same_participant_consecutive_turns=o.max_same_participant_consecutive_turns,
            max_same_team_consecutive_turns=o.max_same_team_consecutive_turns,
            auto_generate_group_report=o.auto_generate_group_report,
            enable_review_workspace=o.enable_review_workspace,
            review_storage_dir=o.review_storage_dir.resolve(),
            reviewer_storage_dir=o.reviewer_storage_dir.resolve(),
            auto_create_review_pack_after_feedback=o.auto_create_review_pack_after_feedback,
            default_review_rubric_id=o.default_review_rubric_id,
            review_queue_max_items=o.review_queue_max_items,
            enable_override_merge=o.enable_override_merge,
            calibration_delta_warn_threshold=o.calibration_delta_warn_threshold,
            enable_curriculum_delivery=o.enable_curriculum_delivery,
            curriculum_pack_builtin_dir=builtin,
            curriculum_custom_pack_dir=o.curriculum_custom_pack_dir.resolve(),
            assignment_storage_dir=o.assignment_storage_dir.resolve(),
            default_curriculum_pack_id=o.default_curriculum_pack_id,
            default_assignment_completion_policy=o.default_assignment_completion_policy,
            auto_attach_session_to_assignment=o.auto_attach_session_to_assignment,
            auto_generate_assignment_report=o.auto_generate_assignment_report,
            enable_plan_to_pack_bridge=o.enable_plan_to_pack_bridge,
            enable_authoring_studio=o.enable_authoring_studio,
            authoring_root_dir=ar,
            authoring_published_runtime_profile_dir=ar / "published" / "runtime_profiles",
            authoring_published_misc_dir=ar / "published" / "artifacts",
            default_author_id=o.default_author_id,
            enable_authoring_preview=o.enable_authoring_preview,
            require_validation_before_publish=o.require_validation_before_publish,
            require_preview_before_publish=o.require_preview_before_publish,
            authoring_max_preview_steps=o.authoring_max_preview_steps,
            authoring_allow_derivative_from_builtin=o.authoring_allow_derivative_from_builtin,
            active_release_profile=getattr(o, "active_release_profile", None) or "v1_demo",
        )


def get_app_config() -> AppConfig:
    return AppConfig.from_env()
