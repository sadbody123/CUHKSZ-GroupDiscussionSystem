"""Aggregate turn-level metrics into session summaries."""

from __future__ import annotations

from typing import Any


def aggregate_turn_metrics(packets: list[dict[str, Any]]) -> dict[str, Any]:
    if not packets:
        return {}
    wpms: list[float] = []
    prs: list[float] = []
    fillers = 0
    dur = 0
    for p in packets:
        m = p.get("metrics") or {}
        if m.get("words_per_minute") is not None:
            wpms.append(float(m["words_per_minute"]))
        if m.get("pause_ratio") is not None:
            prs.append(float(m["pause_ratio"]))
        fillers += int(m.get("filler_count") or 0)
        dur += int(m.get("duration_ms") or 0)
    out: dict[str, Any] = {
        "turns_analyzed": len(packets),
        "total_duration_ms": dur,
        "total_filler_count": fillers,
    }
    if wpms:
        out["mean_words_per_minute"] = round(sum(wpms) / len(wpms), 2)
    if prs:
        out["mean_pause_ratio"] = round(sum(prs) / len(prs), 4)
    return out
