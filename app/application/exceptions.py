"""Application-level exceptions (mapped to HTTP in API layer)."""


class AppError(Exception):
    """Base error for application services."""

    code = "app_error"


class SnapshotNotFoundError(AppError):
    code = "snapshot_not_found"


class TopicNotFoundError(AppError):
    code = "topic_not_found"


class SessionNotFoundError(AppError):
    code = "session_not_found"


class InvalidRequestError(AppError):
    code = "invalid_request"


class PhaseConflictError(AppError):
    """Action not allowed in current session phase."""

    code = "phase_conflict"
