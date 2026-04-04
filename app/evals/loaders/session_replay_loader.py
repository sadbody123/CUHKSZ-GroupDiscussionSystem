"""Load exported session JSON for replay."""

from __future__ import annotations

import json
from pathlib import Path

from app.runtime.schemas.session import SessionContext


def load_session_export(path: Path) -> SessionContext:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SessionContext.model_validate(data)
