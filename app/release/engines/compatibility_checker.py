"""Compatibility check — thin wrapper over readiness."""

from __future__ import annotations

from app.application.config import AppConfig
from app.release.engines.readiness_audit import run_readiness_audit


def check_profile_compatibility(profile_id: str, cfg: AppConfig | None = None) -> dict:
    rep = run_readiness_audit(profile_id, cfg=cfg)
    return {"ok": rep.overall_status != "blocked", "report": rep.model_dump()}
