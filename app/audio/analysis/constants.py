"""Speech delivery proxy analysis — naming and defaults."""

from __future__ import annotations

DEFAULT_PROXY_DISCLAIMER = (
    "These metrics are heuristic / proxy estimates from audio level and transcript text. "
    "They are not pronunciation scores, clinical measures, or standardized tests."
)

ANALYZER_LOCAL_WAVE = "local_wave"
ANALYZER_MOCK_DELIVERY = "mock_delivery"
ANALYZER_ADVANCED_STUB = "advanced_stub"
