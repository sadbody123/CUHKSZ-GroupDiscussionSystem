"""Runtime profile API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ProfileSummaryResponse(BaseModel):
    profile_id: str
    description: str | None = None


class ProfileDetailResponse(BaseModel):
    profile: dict[str, Any]
