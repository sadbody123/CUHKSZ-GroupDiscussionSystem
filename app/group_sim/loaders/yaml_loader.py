"""Load roster templates from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.group_sim.loaders.validators import validate_roster_template
from app.group_sim.schemas.roster import RosterTemplate


class RosterRegistry:
    def __init__(self, templates: dict[str, RosterTemplate]) -> None:
        self._templates = templates

    def get(self, roster_template_id: str) -> RosterTemplate | None:
        return self._templates.get(roster_template_id)

    def list_ids(self) -> list[str]:
        return sorted(self._templates.keys())

    def all_templates(self) -> dict[str, RosterTemplate]:
        return dict(self._templates)


def _load_dir(directory: Path) -> dict[str, RosterTemplate]:
    out: dict[str, RosterTemplate] = {}
    if not directory.is_dir():
        return out
    for path in sorted(directory.glob("*.yaml")):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            t = validate_roster_template(raw)
            out[t.roster_template_id] = t
        except Exception:
            continue
    return out


_REGISTRY: RosterRegistry | None = None


def get_roster_registry(*, template_dir: Path | None = None) -> RosterRegistry:
    global _REGISTRY
    if template_dir is not None:
        return RosterRegistry(_load_dir(template_dir))
    if _REGISTRY is None:
        from app.group_sim.config import roster_template_dir

        _REGISTRY = RosterRegistry(_load_dir(roster_template_dir()))
    return _REGISTRY


def reload_roster_registry() -> None:
    global _REGISTRY
    _REGISTRY = None
