"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.application.audio_service import AudioService
from app.application.speech_analysis_service import SpeechAnalysisService
from app.application.config import AppConfig, get_app_config
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.profile_service import ProfileService
from app.application.learner_service import LearnerService
from app.application.mode_service import ModeService
from app.application.group_service import GroupService
from app.application.authoring_service import AuthoringService
from app.application.release_service import ReleaseService
from app.application.handover_service import HandoverService
from app.application.stability_service import StabilityService
from app.application.curriculum_service import CurriculumService
from app.application.review_service import ReviewService
from app.application.runtime_review_service import RuntimeReviewService
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


def get_audio_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> AudioService:
    return AudioService(config, sessions)


def get_speech_analysis_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> SpeechAnalysisService:
    return SpeechAnalysisService(config, sessions)


def get_learner_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> LearnerService:
    return LearnerService(config, sessions)


def get_mode_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> ModeService:
    return ModeService(config, sessions)


def get_group_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> GroupService:
    return GroupService(config, sessions)


def get_review_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> ReviewService:
    return ReviewService(config, sessions)


def get_runtime_review_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> RuntimeReviewService:
    return RuntimeReviewService(config, sessions)


def get_curriculum_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> CurriculumService:
    return CurriculumService(config, sessions)


def get_authoring_service(
    config: Annotated[AppConfig, Depends(get_config)],
    sessions: Annotated[SessionService, Depends(get_session_service)],
) -> AuthoringService:
    return AuthoringService(config, sessions)


def get_release_service(config: Annotated[AppConfig, Depends(get_config)]) -> ReleaseService:
    return ReleaseService(config)


def get_stability_service(config: Annotated[AppConfig, Depends(get_config)]) -> StabilityService:
    return StabilityService(config)


def get_handover_service(config: Annotated[AppConfig, Depends(get_config)]) -> HandoverService:
    return HandoverService(config)
