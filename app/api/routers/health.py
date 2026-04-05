"""Health router."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_config
from app.api.schemas.health import HealthResponse
from app.application.config import AppConfig
from app.ops.settings import get_ops_settings
from app.ops.version import get_app_version

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request, cfg: Annotated[AppConfig, Depends(get_config)]) -> HealthResponse:
    o = get_ops_settings()
    ver = o.app_version or get_app_version()
    rid = getattr(request.state, "request_id", None)
    return HealthResponse(
        status="ok",
        version=ver,
        default_provider=cfg.default_provider,
        default_snapshot_dir=str(cfg.snapshot_root.resolve()),
        app_env=o.app_env,
        app_version=ver,
        default_runtime_profile=cfg.default_runtime_profile,
        request_id=rid,
    )
