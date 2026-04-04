"""Rule-based ranking for pedagogy and evidence rows."""

from __future__ import annotations

from app.runtime.retrieval import filters
from app.runtime.schemas.query import EvidenceQuery, PedagogyQuery
from app.schemas.evidence_index import EvidenceIndexItem
from app.schemas.pedagogy import PedagogyItem


def _source_weight(source_type: str) -> float:
    s = source_type.lower()
    if "official" in s or "report" in s:
        return 1.0
    if "research" in s or "encyclopedia" in s or "knowledge" in s:
        return 0.85
    if "community" in s:
        return 0.65
    return 0.7


def rank_evidence(items: list[EvidenceIndexItem], q: EvidenceQuery) -> list[EvidenceIndexItem]:
    """Sort by topic match, credibility, quality, keyword, source weight."""

    def score(ev: EvidenceIndexItem) -> float:
        s = 0.0
        if q.topic_tag and filters.evidence_matches_topic_tag(ev, q.topic_tag):
            s += 4.0
        if q.topic_id:
            rel = str(ev.metadata.get("topic_id", ""))
            if q.topic_id in rel:
                s += 2.0
        s += 2.5 * float(ev.credibility_score or 0.0)
        s += 2.0 * float(ev.quality_score or 0.0)
        if q.keyword:
            s += 0.4 * min(5, filters.keyword_hits(ev.text + " " + (ev.title or ""), q.keyword))
        s += 0.5 * _source_weight(ev.source_type)
        if q.stance_hint and (ev.stance_hint or "") == q.stance_hint:
            s += 0.8
        return s

    ranked = sorted(items, key=score, reverse=True)
    if q.top_k:
        return ranked[: q.top_k]
    return ranked


def rank_pedagogy(items: list[PedagogyItem], q: PedagogyQuery) -> list[PedagogyItem]:
    def score(p: PedagogyItem) -> float:
        s = 0.0
        if q.item_type and p.item_type.lower() == q.item_type.lower():
            s += 3.0
        if q.category and (p.category or "").lower() == q.category.lower():
            s += 2.0
        if q.tags:
            pt = {t.lower() for t in p.tags}
            qt = {t.lower() for t in q.tags}
            s += 1.5 * len(pt.intersection(qt))
        if q.session_phase:
            blob = (p.content + " " + str(p.metadata)).lower()
            if q.session_phase.lower() in blob:
                s += 0.5
        return s

    ranked = sorted(items, key=score, reverse=True)
    if q.top_k:
        return ranked[: q.top_k]
    return ranked
