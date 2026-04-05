"""Map signals to coarse rubric dimensions (labels only)."""

from __future__ import annotations

from typing import Any


def rubric_tags_for_signals(signals: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {
        "Fluency": [],
        "Delivery": [],
        "Pronunciation clarity (proxy)": [],
        "Volume / pace (proxy)": [],
    }
    for s in signals:
        sid = str(s.get("signal_id", ""))
        msg = str(s.get("message", ""))
        if "pause" in sid or "pause" in msg.lower():
            out["Fluency"].append(sid)
        if "filler" in sid:
            out["Delivery"].append(sid)
        if "rate" in sid or "wpm" in sid:
            out["Volume / pace (proxy)"].append(sid)
        if "volume" in sid or "rms" in msg.lower():
            out["Volume / pace (proxy)"].append(sid)
        if "confidence" in sid or "pronunciation" in msg.lower():
            out["Pronunciation clarity (proxy)"].append(sid)
    return {k: list(dict.fromkeys(v)) for k, v in out.items() if v}
