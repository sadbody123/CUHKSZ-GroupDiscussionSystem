"""Source catalog repository (read-only)."""

from __future__ import annotations

from app.schemas.source import SourceRecord


class SourceRepository:
    def __init__(self, rows: list[SourceRecord]) -> None:
        self._rows = list(rows)

    def list_sources(self) -> list[SourceRecord]:
        return list(self._rows)

    def by_table(self, source_table: str) -> list[SourceRecord]:
        st = source_table.lower().strip()
        return [r for r in self._rows if r.source_table.lower() == st]
