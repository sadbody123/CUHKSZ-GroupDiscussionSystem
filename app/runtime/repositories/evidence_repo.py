"""Evidence index repository (read-only)."""

from __future__ import annotations

from app.schemas.evidence_index import EvidenceIndexItem


class EvidenceRepository:
    def __init__(self, items: list[EvidenceIndexItem]) -> None:
        self._items = list(items)

    def get_by_evidence_id(self, evidence_id: str) -> EvidenceIndexItem | None:
        for e in self._items:
            if e.evidence_id == evidence_id:
                return e
        return None

    def list_evidence(self) -> list[EvidenceIndexItem]:
        return list(self._items)

    def by_topic(self, topic_id_or_tag: str) -> list[EvidenceIndexItem]:
        key = topic_id_or_tag.strip().lower()
        if not key:
            return []
        out: list[EvidenceIndexItem] = []
        for e in self._items:
            tags = [t.lower() for t in e.topic_tags]
            if key in tags:
                out.append(e)
                continue
            if key in e.metadata.get("topic_id", "").lower():
                out.append(e)
        return out

    def filter(
        self,
        *,
        source_type: str | None = None,
        evidence_type: str | None = None,
        min_quality: float | None = None,
        min_credibility: float | None = None,
        stance_hint: str | None = None,
        top_k: int | None = None,
    ) -> list[EvidenceIndexItem]:
        out: list[EvidenceIndexItem] = []
        for e in self._items:
            if source_type and e.source_type != source_type:
                continue
            if evidence_type and e.evidence_type != evidence_type:
                continue
            if min_quality is not None and (e.quality_score or 0) < min_quality:
                continue
            if min_credibility is not None and (e.credibility_score or 0) < min_credibility:
                continue
            if stance_hint and (e.stance_hint or "") != stance_hint:
                continue
            out.append(e)
            if top_k is not None and len(out) >= top_k:
                break
        return out if top_k is None else out[: top_k]

    def by_doc_id(self, doc_id: str) -> list[EvidenceIndexItem]:
        return [e for e in self._items if e.doc_id == doc_id]
