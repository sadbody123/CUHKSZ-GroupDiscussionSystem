"""FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.middleware.request_context import RequestContextMiddleware
from app.api.routers import handover as handover_router
from app.api.routers import stability as stability_router
from app.api.routers import audio as audio_router
from app.api.routers import speech as speech_router
from app.api.routers import feedback as feedback_router
from app.api.routers import authoring, curriculum, health, learners, modes, profiles, reviews, roster_templates, sessions, snapshots, system, topics
from app.ops.version import get_app_version


def create_app() -> FastAPI:
    app = FastAPI(title="CUHKSZ Group Discussion API", version=get_app_version())
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(system.router)
    app.include_router(stability_router.router)
    app.include_router(handover_router.router)
    app.include_router(snapshots.router)
    app.include_router(modes.router)
    app.include_router(roster_templates.router)
    app.include_router(profiles.router)
    app.include_router(topics.router)
    app.include_router(sessions.router)
    app.include_router(learners.router)
    app.include_router(feedback_router.router)
    app.include_router(audio_router.router)
    app.include_router(speech_router.router)
    app.include_router(reviews.router)
    app.include_router(curriculum.router)
    app.include_router(authoring.router)
    return app


app = create_app()
