"""Load PracticeMode / ScenarioPreset / DrillSpec / AssessmentTemplate from YAML."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from app.modes.config import ModesPaths, get_modes_paths
from app.modes.schemas.assessment import AssessmentTemplate
from app.modes.schemas.drill import DrillSpec
from app.modes.schemas.mode import PracticeMode
from app.modes.schemas.preset import ScenarioPreset

log = logging.getLogger(__name__)


_ID_FIELD: dict[type, str] = {}


def _id_field(model: type) -> str:
    if model not in _ID_FIELD:
        # first field ending with _id in model
        for name in model.model_fields:
            if name.endswith("_id"):
                _ID_FIELD[model] = name
                break
        else:
            _ID_FIELD[model] = list(model.model_fields.keys())[0]
    return _ID_FIELD[model]


def _load_dir(pattern: str, model: type, directory: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not directory.is_dir():
        log.warning("modes directory missing: %s", directory)
        return out
    id_name = _id_field(model)
    for path in sorted(directory.glob(pattern)):
        if not path.is_file():
            continue
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            obj = model.model_validate(raw)
            key = str(getattr(obj, id_name))
            out[key] = obj
        except (OSError, yaml.YAMLError, ValueError) as e:
            log.warning("skip invalid mode file %s: %s", path, e)
    return out


class ModeRegistry:
    """In-memory registry; load once per process."""

    def __init__(self, paths: ModesPaths | None = None) -> None:
        self._paths = paths or get_modes_paths()
        self._modes = _load_dir("*.yaml", PracticeMode, self._paths.practice_modes_dir)
        self._presets = _load_dir("*.yaml", ScenarioPreset, self._paths.presets_dir)
        self._drills = _load_dir("*.yaml", DrillSpec, self._paths.drills_dir)
        self._templates = _load_dir("*.yaml", AssessmentTemplate, self._paths.assessment_templates_dir)

    @property
    def modes(self) -> dict[str, PracticeMode]:
        return self._modes

    @property
    def presets(self) -> dict[str, ScenarioPreset]:
        return self._presets

    @property
    def drills(self) -> dict[str, DrillSpec]:
        return self._drills

    @property
    def assessment_templates(self) -> dict[str, AssessmentTemplate]:
        return self._templates

    def get_mode(self, mode_id: str) -> PracticeMode | None:
        return self._modes.get(mode_id)

    def get_preset(self, preset_id: str) -> ScenarioPreset | None:
        return self._presets.get(preset_id)

    def get_drill(self, drill_id: str) -> DrillSpec | None:
        return self._drills.get(drill_id)

    def get_template(self, template_id: str) -> AssessmentTemplate | None:
        return self._templates.get(template_id)


_REGISTRY: ModeRegistry | None = None


def get_mode_registry() -> ModeRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ModeRegistry()
    return _REGISTRY


def reload_mode_registry() -> ModeRegistry:
    global _REGISTRY
    _REGISTRY = ModeRegistry()
    return _REGISTRY
