"""Topic recommendations from weak skills + practice history."""

from __future__ import annotations

from pathlib import Path

from app.learner.schemas.recommendation import RecommendationItem
from app.runtime.retrieval.router import build_repositories
from app.runtime.snapshot_loader import load_snapshot

# skill_id -> keywords matched against topic tags / summary (lowercase)
WEAK_SKILL_TOPIC_HINTS: dict[str, tuple[str, ...]] = {
    "example_usage": ("example", "sample", "case", "illustrat"),
    "interaction": ("interact", "debate", "discuss", "dialog"),
    "discussion_language": ("language", "phrase", "academic"),
    "turn_concision": ("concise", "brief", "summary"),
    "content_support": ("evidence", "argument", "support"),
    "teammate_support": ("team", "peer", "collaborat"),
    "topic_focus": ("focus", "stance", "claim"),
    "rebuttal_clarity": ("counter", "rebut", "objection"),
    "fluency_proxy": ("oral", "speak", "voice"),
    "pause_management_proxy": ("oral", "speak", "pause"),
}


def select_topic_recommendations(
    snapshot_dir: Path,
    *,
    weak_skills: list[str],
    practiced_topic_ids: set[str],
    max_items: int = 5,
) -> list[RecommendationItem]:
    b = load_snapshot(snapshot_dir)
    _ped, top, _ev, _doc, _src = build_repositories(b)
    cards = top.list_topics()
    scored: list[tuple[float, object]] = []
    for c in cards:
        if c.topic_id in practiced_topic_ids:
            continue
        blob = " ".join(
            [
                c.topic or "",
                c.summary or "",
                " ".join(c.tags),
                " ".join(c.example_hints or []),
            ]
        ).lower()
        score = 0.0
        for sk in weak_skills:
            for hint in WEAK_SKILL_TOPIC_HINTS.get(sk, ()):
                if hint in blob:
                    score += 3.0
            if sk.replace("_", " ") in blob:
                score += 1.0
        if len(c.example_hints or []) > 0:
            score += 1.5
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    out: list[RecommendationItem] = []
    for i, (sc, c) in enumerate(scored[:max_items]):
        if sc <= 0 and i > 0:
            break
        primary_weak = weak_skills[0] if weak_skills else "practice"
        out.append(
            RecommendationItem(
                recommendation_id=f"topic_{c.topic_id}",
                recommendation_type="topic",
                title=f"Practice topic: {c.topic or c.topic_id}",
                reason=(
                    f"Selected to reinforce '{primary_weak}' using topic tags and hints "
                    f"(score={sc:.1f}; heuristic)."
                ),
                priority="high" if i == 0 else "medium",
                linked_topic_ids=[c.topic_id],
                linked_pedagogy_item_ids=[],
                suggested_runtime_profile_id=None,
                suggested_mode=None,
                metadata={"topic_id": c.topic_id, "score": sc},
            )
        )
    if not out and cards:
        c = cards[0]
        out.append(
            RecommendationItem(
                recommendation_id=f"topic_{c.topic_id}_default",
                recommendation_type="topic",
                title=f"Practice topic: {c.topic or c.topic_id}",
                reason="Default topic pick when no weak-skill match is available.",
                priority="medium",
                linked_topic_ids=[c.topic_id],
                linked_pedagogy_item_ids=[],
                suggested_runtime_profile_id=None,
                suggested_mode=None,
                metadata={},
            )
        )
    return out
