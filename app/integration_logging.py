"""Log failures from optional integration hooks without breaking core flows."""

from __future__ import annotations

import logging
from typing import Any

_logger = logging.getLogger(__name__)


def warn_optional_hook_failed(component: str, exc: BaseException, **context: Any) -> None:
    """Record a non-fatal error from a secondary hook (mode, learner, group sim, artifacts, etc.)."""
    if context:
        bits = " ".join(f"{k}={v!r}" for k, v in context.items() if v is not None)
        _logger.warning("Optional hook %r failed (%s): %s", component, bits, exc)
    else:
        _logger.warning("Optional hook %r failed: %s", component, exc)
