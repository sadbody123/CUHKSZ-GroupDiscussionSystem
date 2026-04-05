"""Known filesystem locations for artifact scanning."""

from __future__ import annotations

from pathlib import Path

from app.ops.settings import UnifiedSettings, get_ops_settings


def snapshot_root(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).snapshot_root.resolve()


def session_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).session_storage_dir.resolve()


def eval_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).eval_report_dir.resolve()


def feedback_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).feedback_report_dir.resolve()


def bundle_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).bundle_dir.resolve()


def audio_storage_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).audio_storage_dir.resolve()


def speech_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).speech_report_dir.resolve()


def learner_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).learner_storage_dir.resolve()


def mode_reports_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).mode_reports_dir.resolve()


def group_reports_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).group_reports_dir.resolve()


def review_storage_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).review_storage_dir.resolve()


def reviewer_storage_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).reviewer_storage_dir.resolve()


def curriculum_custom_pack_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).curriculum_custom_pack_dir.resolve()


def assignment_storage_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).assignment_storage_dir.resolve()


def authoring_root(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).authoring_root_dir.resolve()


def release_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).release_report_dir.resolve()


def demo_bundle_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).demo_bundle_dir.resolve()


def stability_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).stability_report_dir.resolve()


def consistency_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).consistency_report_dir.resolve()


def e2e_results_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).e2e_results_dir.resolve()


def rc_report_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).rc_report_dir.resolve()


def handover_manifest_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).release_manifest_dir.resolve()


def final_release_packages_dir(s: UnifiedSettings | None = None) -> Path:
    return (s or get_ops_settings()).final_release_dir.resolve()
