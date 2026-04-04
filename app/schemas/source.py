"""Source catalog entries (per table / file)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SourceRecord(BaseModel):
    """Summary of imported upstream table data."""

    source_table: str
    source_type: str
    source_file: str | None = None
    record_count: int = Field(ge=0)
    notes: list[str] | None = None
