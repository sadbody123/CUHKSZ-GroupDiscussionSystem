"""Topics."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_topic_service
from app.api.schemas.topic import TopicDetailResponse, TopicSummaryResponse
from app.application.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=list[TopicSummaryResponse])
def list_topics(
    svc: Annotated[TopicService, Depends(get_topic_service)],
    snapshot_id: str = Query(..., description="Snapshot folder name under snapshot root"),
    keyword: str | None = Query(None),
) -> list[TopicSummaryResponse]:
    rows = svc.list_topic_summaries(snapshot_id, keyword=keyword)
    return [TopicSummaryResponse(**r) for r in rows]


@router.get("/{topic_id}", response_model=TopicDetailResponse)
def get_topic(
    topic_id: str,
    svc: Annotated[TopicService, Depends(get_topic_service)],
    snapshot_id: str = Query(...),
) -> TopicDetailResponse:
    card = svc.get_topic_detail(snapshot_id, topic_id)
    return TopicDetailResponse(card=card)
