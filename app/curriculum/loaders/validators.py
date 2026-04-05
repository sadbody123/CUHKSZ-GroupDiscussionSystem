"""Soft validation for curriculum pack references."""

from __future__ import annotations

import logging

from app.curriculum.schemas.pack import CurriculumPack

_LOG = logging.getLogger(__name__)


def validate_pack_refs(pack: CurriculumPack) -> list[str]:
    """Return warning messages; never raises for missing optional ecosystem refs."""
    warnings: list[str] = []
    if not pack.steps:
        warnings.append("pack has no steps")
    for st in pack.steps:
        if not st.topic_id and not st.drill_id and st.step_type not in ("review_reflection", "mixed"):
            warnings.append(f"step {st.step_id} has no topic_id or drill_id")
    for w in warnings:
        _LOG.warning("curriculum_pack %s: %s", pack.pack_id, w)
    pack.metadata.setdefault("validation_warnings", warnings)
    return warnings
