"""Rule-based topic card bootstrap from evidence chunks."""

from __future__ import annotations

from collections import Counter, defaultdict

from app.schemas.evidence import EvidenceChunk
from app.schemas.topic_card import TopicCard


def _covered_tags(manual: list[TopicCard]) -> set[str]:
    cov: set[str] = set()
    for c in manual:
        if c.topic:
            cov.add(c.topic.strip().lower())
        for t in c.tags:
            cov.add(str(t).strip().lower())
    return cov


def bootstrap_topic_cards(
    chunks: list[EvidenceChunk],
    *,
    manual: list[TopicCard] | None = None,
    top_n: int = 12,
    max_hints: int = 3,
) -> list[TopicCard]:
    """
    Pick high-frequency topic_tags and synthesize minimal TopicCard rows.

    Skips tags already covered by a manual card (same tag text as ``topic`` or ``tags``).
    """
    covered = _covered_tags(manual or [])
    tag_counts: Counter[str] = Counter()
    tag_docs: defaultdict[str, set[str]] = defaultdict(set)
    tag_chunks: defaultdict[str, list[str]] = defaultdict(list)

    for ch in chunks:
        for t in ch.topic_tags:
            tt = str(t).strip()
            if not tt:
                continue
            tag_counts[tt] += 1
            tag_docs[tt].add(ch.doc_id)
            if len(tag_chunks[tt]) < max_hints * 4:
                tag_chunks[tt].append(ch.chunk_id)

    out: list[TopicCard] = []
    for tag, _n in tag_counts.most_common(top_n * 2):
        if tag.lower() in covered:
            continue
        hints: list[str] = []
        for ch in chunks:
            if tag in ch.topic_tags and ch.text.strip():
                snippet = ch.text.strip().replace("\n", " ")
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                hints.append(snippet)
                if len(hints) >= max_hints:
                    break
        card = TopicCard(
            topic_id=f"bootstrap:{tag}",
            topic=tag,
            summary=f"Auto-generated card for tag `{tag}` from evidence frequency.",
            tags=[tag],
            related_doc_ids=sorted(tag_docs[tag]),
            related_chunk_ids=tag_chunks[tag][:32],
            example_hints=hints,
            metadata={"bootstrap": True, "source": "topic_tag_frequency"},
        )
        out.append(card)
        if len(out) >= top_n:
            break
    return out


def merge_topic_cards(manual: list[TopicCard], boot: list[TopicCard]) -> list[TopicCard]:
    """Manual cards win; drop bootstrap cards whose topic_id collides."""
    seen: set[str] = {c.topic_id for c in manual}
    merged = list(manual)
    for c in boot:
        if c.topic_id in seen:
            continue
        merged.append(c)
        seen.add(c.topic_id)
    return merged
