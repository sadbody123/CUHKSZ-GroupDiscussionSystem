"""Pipeline entry for readiness."""

from __future__ import annotations

from app.application.config import AppConfig
from app.release.engines.readiness_audit import run_readiness_audit


def run_pipeline(profile_id: str, cfg: AppConfig | None = None):
    return run_readiness_audit(profile_id, cfg=cfg)
