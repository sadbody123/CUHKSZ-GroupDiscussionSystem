"""Normalized document repository (read-only)."""

from __future__ import annotations

from app.schemas.normalized_doc import NormalizedDocument


class DocumentRepository:
    def __init__(self, docs: list[NormalizedDocument]) -> None:
        self._by_id: dict[str, NormalizedDocument] = {d.doc_id: d for d in docs}

    def get_doc(self, doc_id: str) -> NormalizedDocument | None:
        return self._by_id.get(doc_id)

    def get_docs(self, doc_ids: list[str]) -> list[NormalizedDocument]:
        return [d for did in doc_ids if (d := self._by_id.get(did)) is not None]
