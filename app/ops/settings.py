"""Unified runtime settings (.env + environment variables)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.ops.version import get_app_version


def _root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


class UnifiedSettings(BaseSettings):
    """Single settings object for CLI, API, ops, and offline build path defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default="CUHKSZ-GroupDiscussionSystem")
    app_env: str = Field(default="development")
    app_version: str = Field(default_factory=get_app_version)
    log_level: str = Field(default="INFO")

    project_root: Path = Field(default_factory=_root)
    snapshot_root: Path = Field(default_factory=lambda: _root() / "app" / "knowledge" / "snapshots")
    session_storage_dir: Path = Field(default_factory=lambda: _root() / "storage" / "sessions")
    eval_report_dir: Path = Field(default_factory=lambda: _root() / "storage" / "eval_reports")
    feedback_report_dir: Path = Field(default_factory=lambda: _root() / "storage" / "feedback_reports")
    bundle_dir: Path = Field(default_factory=lambda: _root() / "storage" / "bundles")
    audio_storage_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "audio",
        validation_alias="AUDIO_STORAGE_DIR",
    )

    enable_audio: bool = Field(default=True, validation_alias="ENABLE_AUDIO")
    default_asr_provider: str = Field(default="mock_asr", validation_alias="DEFAULT_ASR_PROVIDER")
    default_tts_provider: str = Field(default="mock_tts", validation_alias="DEFAULT_TTS_PROVIDER")
    max_audio_upload_mb: int = Field(default=25, validation_alias="MAX_AUDIO_UPLOAD_MB")
    mock_asr_manifest_path: str | None = Field(default=None, validation_alias="MOCK_ASR_MANIFEST_PATH")
    openai_transcribe_model: str | None = Field(default=None, validation_alias="OPENAI_TRANSCRIBE_MODEL")
    openai_tts_model: str | None = Field(default=None, validation_alias="OPENAI_TTS_MODEL")

    speech_report_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "speech_reports",
        validation_alias="SPEECH_REPORT_DIR",
    )
    enable_speech_analysis: bool = Field(default=True, validation_alias="ENABLE_SPEECH_ANALYSIS")
    default_speech_analyzer: str = Field(default="local_wave", validation_alias="DEFAULT_SPEECH_ANALYZER")
    speech_analysis_default_profile: str = Field(default="speech_default", validation_alias="SPEECH_ANALYSIS_DEFAULT_PROFILE")
    pause_min_duration_ms: int = Field(default=200, validation_alias="PAUSE_MIN_DURATION_MS")
    pause_silence_threshold: float = Field(default=120.0, validation_alias="PAUSE_SILENCE_THRESHOLD")
    target_wpm_min: float = Field(default=80.0, validation_alias="TARGET_WPM_MIN")
    target_wpm_max: float = Field(default=200.0, validation_alias="TARGET_WPM_MAX")
    filler_words_csv: str = Field(default="um,uh,like,you know,actually", validation_alias="FILLER_WORDS")
    confidence_proxy_warn_threshold: float = Field(default=0.45, validation_alias="CONFIDENCE_PROXY_WARN_THRESHOLD")

    default_provider: str = Field(default="mock")
    default_model: str | None = Field(default=None)
    default_runtime_profile: str = Field(default="default")
    agent_runtime_backend: str = Field(default="v1", validation_alias="AGENT_RUNTIME_BACKEND")
    agent_runtime_v2_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "agent_runtime_v2",
        validation_alias="AGENT_RUNTIME_V2_DIR",
    )

    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8000)
    ui_api_base_url: str = Field(default="http://127.0.0.1:8000")

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, validation_alias="OPENAI_BASE_URL")
    openai_model: str | None = Field(default=None, validation_alias="OPENAI_MODEL")

    chunk_size: int = Field(default=600)
    chunk_overlap: int = Field(default=80)
    min_text_chars: int = Field(default=20)

    learner_storage_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "learners",
        validation_alias="LEARNER_STORAGE_DIR",
    )
    enable_learner_analytics: bool = Field(default=True, validation_alias="ENABLE_LEARNER_ANALYTICS")
    default_learning_plan_horizon: int = Field(default=4, validation_alias="DEFAULT_LEARNING_PLAN_HORIZON")
    learner_recommendation_max_items: int = Field(default=12, validation_alias="LEARNER_RECOMMENDATION_MAX_ITEMS")
    learner_recent_window: int = Field(default=3, validation_alias="LEARNER_RECENT_WINDOW")
    learner_baseline_window: int = Field(default=3, validation_alias="LEARNER_BASELINE_WINDOW")
    auto_ingest_session_to_learner: bool = Field(default=False, validation_alias="AUTO_INGEST_SESSION_TO_LEARNER")
    enable_learner_ui_panels: bool = Field(default=True, validation_alias="ENABLE_LEARNER_UI_PANELS")

    enable_practice_modes: bool = Field(default=True, validation_alias="ENABLE_PRACTICE_MODES")
    mode_asset_root: Path | None = Field(default=None, validation_alias="MODE_ASSET_ROOT")
    mode_reports_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "mode_reports",
        validation_alias="MODE_REPORTS_DIR",
    )
    default_mode_id: str = Field(default="free_practice", validation_alias="DEFAULT_MODE_ID")
    default_preset_id: str = Field(default="free_practice", validation_alias="DEFAULT_PRESET_ID")
    default_assessment_template_id: str = Field(
        default="gd_assessment_4p_v1",
        validation_alias="DEFAULT_ASSESSMENT_TEMPLATE_ID",
    )
    enable_prep_phase: bool = Field(default=True, validation_alias="ENABLE_PREP_PHASE")
    enable_assessment_timer: bool = Field(default=True, validation_alias="ENABLE_ASSESSMENT_TIMER")
    micro_drill_max_steps: int = Field(default=12, validation_alias="MICRO_DRILL_MAX_STEPS")
    auto_generate_mode_report: bool = Field(default=True, validation_alias="AUTO_GENERATE_MODE_REPORT")

    enable_group_sim: bool = Field(default=True, validation_alias="ENABLE_GROUP_SIM")
    roster_template_dir: Path | None = Field(default=None, validation_alias="ROSTER_TEMPLATE_DIR")
    group_reports_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "group_reports",
        validation_alias="GROUP_REPORTS_DIR",
    )
    default_roster_template_id: str = Field(default="gd_4p_balanced", validation_alias="DEFAULT_ROSTER_TEMPLATE_ID")
    default_4p_roster_template_id: str = Field(default="gd_4p_balanced", validation_alias="DEFAULT_4P_ROSTER_TEMPLATE_ID")
    default_6p_roster_template_id: str = Field(default="gd_6p_balanced", validation_alias="DEFAULT_6P_ROSTER_TEMPLATE_ID")
    enable_balance_warnings: bool = Field(default=True, validation_alias="ENABLE_BALANCE_WARNINGS")
    max_same_participant_consecutive_turns: int = Field(default=2, validation_alias="MAX_SAME_PARTICIPANT_CONSECUTIVE_TURNS")
    max_same_team_consecutive_turns: int = Field(default=2, validation_alias="MAX_SAME_TEAM_CONSECUTIVE_TURNS")
    auto_generate_group_report: bool = Field(default=True, validation_alias="AUTO_GENERATE_GROUP_REPORT")

    enable_review_workspace: bool = Field(default=True, validation_alias="ENABLE_REVIEW_WORKSPACE")
    review_storage_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "reviews",
        validation_alias="REVIEW_STORAGE_DIR",
    )
    reviewer_storage_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "reviewers",
        validation_alias="REVIEWER_STORAGE_DIR",
    )
    auto_create_review_pack_after_feedback: bool = Field(
        default=False,
        validation_alias="AUTO_CREATE_REVIEW_PACK_AFTER_FEEDBACK",
    )
    default_review_rubric_id: str | None = Field(default=None, validation_alias="DEFAULT_REVIEW_RUBRIC_ID")
    review_queue_max_items: int = Field(default=500, validation_alias="REVIEW_QUEUE_MAX_ITEMS")
    enable_override_merge: bool = Field(default=True, validation_alias="ENABLE_OVERRIDE_MERGE")
    calibration_delta_warn_threshold: float = Field(default=0.35, validation_alias="CALIBRATION_DELTA_WARN_THRESHOLD")

    enable_curriculum_delivery: bool = Field(default=True, validation_alias="ENABLE_CURRICULUM_DELIVERY")
    curriculum_pack_builtin_dir: Path | None = Field(default=None, validation_alias="CURRICULUM_PACK_BUILTIN_DIR")
    curriculum_custom_pack_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "curriculum_packs" / "custom",
        validation_alias="CURRICULUM_CUSTOM_PACK_DIR",
    )
    assignment_storage_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "assignments",
        validation_alias="ASSIGNMENT_STORAGE_DIR",
    )
    default_curriculum_pack_id: str = Field(default="foundation_gd_pack", validation_alias="DEFAULT_CURRICULUM_PACK_ID")
    default_assignment_completion_policy: str = Field(default="min_one_step", validation_alias="DEFAULT_ASSIGNMENT_COMPLETION_POLICY")
    auto_attach_session_to_assignment: bool = Field(default=False, validation_alias="AUTO_ATTACH_SESSION_TO_ASSIGNMENT")
    auto_generate_assignment_report: bool = Field(default=False, validation_alias="AUTO_GENERATE_ASSIGNMENT_REPORT")
    enable_plan_to_pack_bridge: bool = Field(default=True, validation_alias="ENABLE_PLAN_TO_PACK_BRIDGE")

    enable_authoring_studio: bool = Field(default=True, validation_alias="ENABLE_AUTHORING_STUDIO")
    authoring_root_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "authoring",
        validation_alias="AUTHORING_ROOT_DIR",
    )
    default_author_id: str = Field(default="author_local", validation_alias="DEFAULT_AUTHOR_ID")
    enable_authoring_preview: bool = Field(default=True, validation_alias="ENABLE_AUTHORING_PREVIEW")
    require_validation_before_publish: bool = Field(default=True, validation_alias="REQUIRE_VALIDATION_BEFORE_PUBLISH")
    require_preview_before_publish: bool = Field(default=False, validation_alias="REQUIRE_PREVIEW_BEFORE_PUBLISH")
    authoring_max_preview_steps: int = Field(default=50, validation_alias="AUTHORING_MAX_PREVIEW_STEPS")
    authoring_allow_derivative_from_builtin: bool = Field(default=True, validation_alias="AUTHORING_ALLOW_DERIVATIVE_FROM_BUILTIN")

    active_release_profile: str = Field(default="v1_demo", validation_alias="ACTIVE_RELEASE_PROFILE")
    release_profile_dir: Path | None = Field(default=None, validation_alias="RELEASE_PROFILE_DIR")
    release_report_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "release" / "reports",
        validation_alias="RELEASE_REPORT_DIR",
    )
    demo_scenario_dir: Path | None = Field(default=None, validation_alias="DEMO_SCENARIO_DIR")
    demo_bundle_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "release" / "bundles",
        validation_alias="DEMO_BUNDLE_DIR",
    )
    enable_release_gating: bool = Field(default=True, validation_alias="ENABLE_RELEASE_GATING")
    enable_experimental_capabilities: bool = Field(default=True, validation_alias="ENABLE_EXPERIMENTAL_CAPABILITIES")
    default_demo_scenario_id: str = Field(default="text_core_demo", validation_alias="DEFAULT_DEMO_SCENARIO_ID")
    require_readiness_before_ui: bool = Field(default=False, validation_alias="REQUIRE_READINESS_BEFORE_UI")
    require_readiness_before_api_demo: bool = Field(default=False, validation_alias="REQUIRE_READINESS_BEFORE_API_DEMO")

    enable_stability_audit: bool = Field(default=True, validation_alias="ENABLE_STABILITY_AUDIT")
    stability_report_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "stability" / "reports",
        validation_alias="STABILITY_REPORT_DIR",
    )
    consistency_report_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "stability" / "consistency",
        validation_alias="CONSISTENCY_REPORT_DIR",
    )
    e2e_results_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "stability" / "e2e_results",
        validation_alias="E2E_RESULTS_DIR",
    )
    known_issues_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "stability" / "issues",
        validation_alias="KNOWN_ISSUES_DIR",
    )
    rc_report_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "stability" / "rc",
        validation_alias="RC_REPORT_DIR",
    )
    e2e_scenario_dir: Path | None = Field(default=None, validation_alias="E2E_SCENARIO_DIR")
    require_green_rc_for_demo_bundle: bool = Field(default=False, validation_alias="REQUIRE_GREEN_RC_FOR_DEMO_BUNDLE")
    run_e2e_on_startup_check: bool = Field(default=False, validation_alias="RUN_E2E_ON_STARTUP_CHECK")
    auto_record_failed_e2e_as_issue: bool = Field(default=False, validation_alias="AUTO_RECORD_FAILED_E2E_AS_ISSUE")

    final_release_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "packages",
        validation_alias="FINAL_RELEASE_DIR",
    )
    release_manifest_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "manifests",
        validation_alias="RELEASE_MANIFEST_DIR",
    )
    bom_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "bom",
        validation_alias="BOM_DIR",
    )
    demo_kit_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "demo_kits",
        validation_alias="DEMO_KIT_DIR",
    )
    handover_kit_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "kits",
        validation_alias="HANDOVER_KIT_DIR",
    )
    acceptance_evidence_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "acceptance",
        validation_alias="ACCEPTANCE_EVIDENCE_DIR",
    )
    final_docs_bundle_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "docs_bundle",
        validation_alias="FINAL_DOCS_BUNDLE_DIR",
    )
    delivery_verification_dir: Path = Field(
        default_factory=lambda: _root() / "storage" / "handover" / "verification",
        validation_alias="DELIVERY_VERIFICATION_DIR",
    )
    default_final_release_profile: str = Field(default="v1_demo", validation_alias="DEFAULT_FINAL_RELEASE_PROFILE")
    require_rc_go_or_conditional_go_for_handover: bool = Field(
        default=False, validation_alias="REQUIRE_RC_GO_OR_CONDITIONAL_GO_FOR_HANDOVER"
    )
    require_acceptance_evidence_before_package: bool = Field(
        default=False, validation_alias="REQUIRE_ACCEPTANCE_EVIDENCE_BEFORE_PACKAGE"
    )
    enable_final_delivery_ui: bool = Field(default=True, validation_alias="ENABLE_FINAL_DELIVERY_UI")

    structured_logging: bool = Field(default=False)


@lru_cache
def get_ops_settings() -> UnifiedSettings:
    return UnifiedSettings()
