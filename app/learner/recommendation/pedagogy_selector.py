"""Map weak skills to pedagogy items."""

from __future__ import annotations

from pathlib import Path

from app.learner.schemas.recommendation import RecommendationItem
from app.runtime.retrieval.router import build_repositories
from app.runtime.snapshot_loader import load_snapshot

SKILL_TAG_MAP: dict[str, tuple[str, ...]] = {
    "example_usage": ("example", "rubric", "language_bank"),
    "interaction": ("interaction", "discussion", "coaching"),
    "discussion_language": ("language_bank", "phrase"),
    "turn_concision": ("coaching", "concise"),
    "fluency_proxy": ("delivery", "oral"),
    "pause_management_proxy": ("delivery", "pause"),
}


def select_pedagogy_recommendations(
    snapshot_dir: Path,
    *,
    weak_skills: list[str],
    max_items: int = 6,
) -> list[RecommendationItem]:
    b = load_snapshot(snapshot_dir)
    ped, _top, _ev, _doc, _src = build_repositories(b)
    want_tags: set[str] = set()
    for sk in weak_skills:
        for t in SKILL_TAG_MAP.get(sk, ("coaching", "tips")):
            want_tags.add(t.lower())
    items = ped.list_items()
    ranked: list[tuple[int, object]] = []
    for it in items:
        it_tags = {t.lower() for t in it.tags}
        overlap = len(want_tags.intersection(it_tags))
        ranked.append((overlap, it))
    ranked.sort(key=lambda x: x[0], reverse=True)
    out: list[RecommendationItem] = []
    for overlap, it in ranked:
        if len(out) >= max_items:
            break
        if overlap == 0 and out:
            break
        out.append(
            RecommendationItem(
                recommendation_id=f"ped_{it.item_id}",
                recommendation_type="pedagogy",
                title=f"{it.item_type}: {it.item_id}",
                reason=f"Tag overlap with weak skills ({overlap}) — {it.category or 'general'} content.",
                priority="high" if overlap > 0 else "low",
                linked_topic_ids=[],
                linked_pedagogy_item_ids=[it.item_id],
                suggested_runtime_profile_id=None,
                suggested_mode=None,
                metadata={"item_type": it.item_type},
            )
        )
    if not out and items:
        for it in items[:max_items]:
            out.append(
                RecommendationItem(
                    recommendation_id=f"ped_{it.item_id}",
                    recommendation_type="pedagogy",
                    title=f"{it.item_type}: {it.item_id}",
                    reason="General pedagogy item (no tag overlap — baseline pick).",
                    priority="low",
                    linked_topic_ids=[],
                    linked_pedagogy_item_ids=[it.item_id],
                    suggested_runtime_profile_id=None,
                    suggested_mode=None,
                    metadata={"item_type": it.item_type, "fallback": True},
                )
            )
    return out
