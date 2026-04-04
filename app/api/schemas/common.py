"""Shared API response helpers."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    code: str = "error"
    detail: str | None = None


class MessageOk(BaseModel):
    ok: bool = True
