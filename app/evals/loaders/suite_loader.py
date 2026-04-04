"""Load eval suite YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.evals.schemas.suite import EvalSuite


def load_suite(path: Path) -> EvalSuite:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return EvalSuite.model_validate(raw)
