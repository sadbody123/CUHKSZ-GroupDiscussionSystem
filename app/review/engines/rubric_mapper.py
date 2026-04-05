"""Map pedagogy rubric items to review dimensions (deterministic)."""

from __future__ import annotations

import logging
from pathlib import Path

from app.review.schemas.rubric import RubricDimension
from app.runtime.retrieval.router import build_repositories
from app.runtime.snapshot_loader import load_snapshot
from app.schemas.pedagogy import PedagogyItem

_logger = logging.getLogger(__name__)

_FALLBACK: list[RubricDimension] = [
    RubricDimension(dimension_id="content", dimension_name="Content quality", max_score=5.0, source="fallback"),
    RubricDimension(dimension_id="interaction", dimension_name="Interaction & turn-taking", max_score=5.0, source="fallback"),
    RubricDimension(
        dimension_id="discussion_language",
        dimension_name="Discussion language",
        max_score=5.0,
        source="fallback",
    ),
    RubricDimension(
        dimension_id="support_and_examples",
        dimension_name="Support & examples",
        max_score=5.0,
        source="fallback",
    ),
    RubricDimension(
        dimension_id="fluency_proxy",
        dimension_name="Fluency (speech proxy, if applicable)",
        max_score=5.0,
        source="fallback",
    ),
    RubricDimension(
        dimension_id="delivery_proxy",
        dimension_name="Delivery (speech proxy, if applicable)",
        max_score=5.0,
        source="fallback",
    ),
    RubricDimension(
        dimension_id="balance_and_coordination",
        dimension_name="Balance & coordination (group proxy, if applicable)",
        max_score=5.0,
        source="fallback",
    ),
]


def _tag_bucket(tags: list[str], category: str | None) -> str | None:
    tset = {x.lower() for x in tags}
    cat = (category or "").lower()
    if "group" in tset or "balance" in tset or "coordination" in cat:
        return "balance_and_coordination"
    if "fluency" in tset or "oral" in tset:
        return "fluency_proxy"
    if "delivery" in tset or "pause" in tset:
        return "delivery_proxy"
    if "interaction" in tset or "discussion" in cat:
        return "interaction"
    if "language" in tset or "phrase" in tset:
        return "discussion_language"
    if "example" in tset or "evidence" in tset:
        return "support_and_examples"
    if "content" in tset or "argument" in tset:
        return "content"
    return None


def map_pedagogy_rubric_items(items: list[PedagogyItem]) -> list[RubricDimension]:
    """Deterministically derive dimensions from rubric pedagogy rows."""
    dims: dict[str, RubricDimension] = {}
    for it in items:
        if it.item_type.lower() != "rubric":
            continue
        bucket = _tag_bucket(it.tags, it.category) or "content"
        did = f"pedagogy_{bucket}"
        if did in dims:
            # merge description
            prev = dims[did]
            desc = (prev.description or "") + " | " + (it.content[:200] if it.content else "")
            dims[did] = RubricDimension(
                dimension_id=did,
                dimension_name=prev.dimension_name,
                max_score=prev.max_score,
                description=desc[:2000],
                source="pedagogy",
                metadata={"item_ids": prev.metadata.get("item_ids", []) + [it.item_id]},
            )
        else:
            dims[did] = RubricDimension(
                dimension_id=did,
                dimension_name=(it.category or bucket).replace("_", " ").title(),
                max_score=float(it.metadata.get("max_score", 5)) if isinstance(it.metadata.get("max_score"), (int, float)) else 5.0,
                description=it.content[:2000] if it.content else None,
                source="pedagogy",
                metadata={"item_ids": [it.item_id]},
            )
    if dims:
        return [dims[k] for k in sorted(dims.keys())]
    return list(_FALLBACK)


def build_rubric_dimensions_for_snapshot(snapshot_dir: Path | None) -> list[RubricDimension]:
    if not snapshot_dir:
        return list(_FALLBACK)
    p = Path(snapshot_dir)
    if not p.is_dir():
        return list(_FALLBACK)
    try:
        b = load_snapshot(p)
        ped, _t, _e, _d, _s = build_repositories(b)
        rub = ped.get_by_type("rubric")
        if rub:
            return map_pedagogy_rubric_items(rub)
    except Exception as exc:
        _logger.warning(
            "Rubric mapping from snapshot failed; using fallback dimensions (%s): %s",
            snapshot_dir,
            exc,
        )
    return list(_FALLBACK)
