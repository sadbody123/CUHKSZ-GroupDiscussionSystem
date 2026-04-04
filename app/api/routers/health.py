"""Health router."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_config
from app.api.schemas.health import HealthResponse
from app.application.config import AppConfig

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(cfg: Annotated[AppConfig, Depends(get_config)]) -> HealthResponse:
    try:
        from importlib.metadata import version

        ver = version("cuhksz-group-discussion-system")
    except Exception:
        ver = "0.1.0"
    return HealthResponse(
        status="ok",
        version=ver,
        default_provider=cfg.default_provider,
        default_snapshot_dir=str(cfg.snapshot_root.resolve()),
    )
