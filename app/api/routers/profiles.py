"""Runtime profiles."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_profile_service
from app.api.schemas.profiles import ProfileDetailResponse, ProfileSummaryResponse
from app.application.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=list[ProfileSummaryResponse])
def list_profiles(svc: Annotated[ProfileService, Depends(get_profile_service)]) -> list[ProfileSummaryResponse]:
    rows = svc.list_profiles()
    return [ProfileSummaryResponse(**r) for r in rows]


@router.get("/{profile_id}", response_model=ProfileDetailResponse)
def get_profile(
    profile_id: str,
    svc: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileDetailResponse:
    data = svc.get_profile(profile_id)
    return ProfileDetailResponse(profile=data)
