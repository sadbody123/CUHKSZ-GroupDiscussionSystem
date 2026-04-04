"""Optional transcript analysis-only endpoint (uses same FeedbackService)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_feedback_service
from app.application.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/sessions/{session_id}/analyze")
def analyze_transcript(
    session_id: str,
    fb: Annotated[FeedbackService, Depends(get_feedback_service)],
) -> dict:
    """Return structured FeedbackPacket JSON without coach narrative."""
    return fb.analyze_transcript(session_id)
