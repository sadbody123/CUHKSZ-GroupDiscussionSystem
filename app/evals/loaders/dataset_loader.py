"""Load eval cases by id from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.evals.config import cases_search_roots
from app.evals.schemas.case import EvalCase

_INDEX: dict[str, EvalCase] | None = None


def _build_index() -> dict[str, EvalCase]:
    out: dict[str, EvalCase] = {}
    for root in cases_search_roots():
        if not root.is_dir():
            continue
        for path in root.glob("*.yaml"):
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for c in raw.get("cases", []) or []:
                case = EvalCase.model_validate(c)
                out[case.case_id] = case
    return out


def load_case(case_id: str) -> EvalCase:
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    if case_id not in _INDEX:
        raise KeyError(f"Unknown eval case: {case_id}")
    return _INDEX[case_id]


def reload_cases() -> None:
    global _INDEX
    _INDEX = None
