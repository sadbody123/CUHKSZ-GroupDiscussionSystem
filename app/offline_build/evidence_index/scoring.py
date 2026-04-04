"""Rule-based stance, credibility, and quality scoring."""

from __future__ import annotations

import re

from app.schemas.evidence import EvidenceChunk
from app.schemas.normalized_doc import NormalizedDocument

_FOR_PAT = re.compile(
    r"(?i)\b(support|pro\b|favor|endorse|赞成|支持|有利于|赞同)\b"
)
_AGAINST_PAT = re.compile(
    r"(?i)\b(against|oppose|reject|refute|反对|不利于|批评|质疑)\b"
)
_MIXED_PAT = re.compile(r"(?i)\b(however|but\b|虽然|但是|然而)\b")


def infer_stance_hint(
    chunk: EvidenceChunk,
    doc: NormalizedDocument | None,
    *,
    source_table: str,
) -> str:
    text = f"{doc.title if doc else ''}\n{chunk.text}"
    fhit = bool(_FOR_PAT.search(text))
    ahit = bool(_AGAINST_PAT.search(text))
    if fhit and ahit:
        return "mixed" if _MIXED_PAT.search(chunk.text) else "mixed"
    if fhit:
        return "for"
    if ahit:
        return "against"
    st = source_table.lower()
    if st.startswith("community"):
        return "neutral"
    if st in ("reports", "encyclopedia_entries", "research_outputs"):
        return "neutral"
    return "unknown"


def credibility_score(
    *,
    source_table: str,
    source_type: str,
) -> float:
    """Layered heuristic in [0, 1]."""
    st = source_table.lower()
    if st == "reports" or "official" in source_type.lower():
        return 0.92
    if st in ("research_outputs", "encyclopedia_entries", "research_projects", "knowledge_entities"):
        return 0.78
    if st.startswith("community"):
        return 0.55
    return 0.65


def quality_score(
    chunk: EvidenceChunk,
    doc: NormalizedDocument | None,
    *,
    base_quality: float | None,
) -> float:
    """
    Improve chunk quality with simple length / metadata signals.

    If base_quality is set (from phase-1 chunker), blend it with heuristics.
    """
    q = 0.55
    if base_quality is not None:
        q = 0.5 * float(base_quality) + 0.5 * q
    L = len(chunk.text.strip())
    if L > 400:
        q += 0.08
    elif L > 120:
        q += 0.04
    if doc and doc.url:
        q += 0.05
    if doc and doc.title:
        q += 0.03
    if chunk.topic_tags:
        q += min(0.05, 0.01 * len(chunk.topic_tags))
    return max(0.0, min(1.0, round(q, 4)))
