"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.application.config import AppConfig, get_app_config
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.profile_service import ProfileService
from app.application.session_service import SessionService
from app.application.snapshot_service import SnapshotService
from app.application.topic_service import TopicService


def get_config() -> AppConfig:
    return get_app_config()


def get_session_service(config: Annotated[AppConfig, Depends(get_config)]) -> SessionService:
    return SessionService(config)


def get_snapshot_service(config: Annotated[AppConfig, Depends(get_config)]) -> SnapshotService:
    return SnapshotService(config)


def get_topic_service(config: Annotated[AppConfig, Depends(get_config)]) -> TopicService:
    return TopicService(config)


def get_discussion_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> DiscussionService:
    return DiscussionService(config, sessions)


def get_feedback_service(
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> FeedbackService:
    return FeedbackService(sessions)


def get_profile_service() -> ProfileService:
    return ProfileService()
