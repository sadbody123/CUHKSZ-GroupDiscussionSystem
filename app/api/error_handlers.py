"""Map application exceptions to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application import exceptions as appx
from app.ops.trace import get_request_id


def _body(payload: dict) -> dict:
    rid = get_request_id()
    if rid:
        return {**payload, "request_id": rid}
    return payload


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(appx.SnapshotNotFoundError)
    async def _snap(_: Request, exc: appx.SnapshotNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=_body(
                {"error": "snapshot_not_found", "code": appx.SnapshotNotFoundError.code, "detail": str(exc)}
            ),
        )

    @app.exception_handler(appx.TopicNotFoundError)
    async def _topic(_: Request, exc: appx.TopicNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=_body({"error": "topic_not_found", "code": appx.TopicNotFoundError.code, "detail": str(exc)}),
        )

    @app.exception_handler(appx.SessionNotFoundError)
    async def _sess(_: Request, exc: appx.SessionNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=_body({"error": "session_not_found", "code": appx.SessionNotFoundError.code, "detail": str(exc)}),
        )

    @app.exception_handler(appx.InvalidRequestError)
    async def _bad(_: Request, exc: appx.InvalidRequestError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_body({"error": "invalid_request", "code": appx.InvalidRequestError.code, "detail": str(exc)}),
        )

    @app.exception_handler(appx.PhaseConflictError)
    async def _phase(_: Request, exc: appx.PhaseConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=_body({"error": "phase_conflict", "code": appx.PhaseConflictError.code, "detail": str(exc)}),
        )
