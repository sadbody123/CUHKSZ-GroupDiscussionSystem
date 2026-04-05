"""Validate roster template payloads."""

from __future__ import annotations

from app.group_sim.schemas.roster import RosterTemplate


def validate_roster_template(raw: dict) -> RosterTemplate:
    return RosterTemplate.model_validate(raw)


def default_roster_template_id() -> str:
    from app.ops.settings import get_ops_settings

    s = get_ops_settings()
    return getattr(s, "default_roster_template_id", None) or "gd_4p_balanced"
