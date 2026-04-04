"""FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.routers import feedback as feedback_router
from app.api.routers import health, profiles, sessions, snapshots, topics


def create_app() -> FastAPI:
    app = FastAPI(title="CUHKSZ Group Discussion API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(snapshots.router)
    app.include_router(profiles.router)
    app.include_router(topics.router)
    app.include_router(sessions.router)
    app.include_router(feedback_router.router)
    return app


app = create_app()
