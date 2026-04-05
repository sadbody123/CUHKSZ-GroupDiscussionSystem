"""Pipeline wrapper for E2E matrix."""

from __future__ import annotations

from pathlib import Path

from app.application.config import AppConfig, get_app_config
from app.stability.engines.scenario_orchestrator import run_e2e_matrix


def run_e2e_matrix_pipeline(
    *,
    profile_id: str,
    snapshot_id: str,
    topic_id: str,
    provider_name: str = "mock",
    cfg: AppConfig | None = None,
    scenario_ids: list[str] | None = None,
    e2e_scenario_dir: Path | None = None,
):
    cfg = cfg or get_app_config()
    return run_e2e_matrix(
        profile_id=profile_id,
        snapshot_id=snapshot_id,
        topic_id=topic_id,
        provider_name=provider_name,
        cfg=cfg,
        scenario_ids=scenario_ids,
        e2e_scenario_dir=e2e_scenario_dir,
    )
