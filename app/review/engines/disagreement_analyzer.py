"""Deterministic mismatch / disagreement tagging."""

from __future__ import annotations

from typing import Any


def _norm_set(items: list[Any] | None) -> set[str]:
    out: set[str] = set()
    for x in items or []:
        s = str(x).strip().lower()
        if s:
            out.add(s)
    return out


def analyze_strength_risk_overlap(
    ai_strengths: list[str],
    ai_risks: list[str],
    human_notes: list[str],
) -> dict[str, list[str]]:
    """Classify overlap between AI lists and free-text human notes (token-light)."""
    hs = " ".join(human_notes).lower()
    ai_s = _norm_set(ai_strengths)
    ai_r = _norm_set(ai_risks)
    ai_miss_risk: list[str] = []
    ai_false_risk: list[str] = []
    human_only: list[str] = []
    for r in ai_r:
        if r and r not in hs and not any(tok in hs for tok in r.split() if len(tok) > 3):
            ai_miss_risk.append(r)
    for s in ai_s:
        if s and any(w in hs for w in ("risk", "weak", "issue", "problem")) and s in hs:
            ai_false_risk.append(s)
    for line in human_notes:
        low = line.lower()
        if not any(low in a for a in ai_s) and "risk" in low:
            human_only.append(line.strip())
    return {
        "ai_missing_risk_in_human_view": ai_miss_risk,
        "ai_possible_false_positive_strength": ai_false_risk,
        "human_added_risk_or_concern": human_only,
    }


def tag_proxy_overreliance(coach_report: dict[str, Any] | None) -> list[str]:
    out: list[str] = []
    if not coach_report:
        return out
    if coach_report.get("speech_report"):
        out.append("ai_coach_embedded_speech_proxy")
    pl = coach_report.get("proxy_limitations") or []
    if not pl:
        out.append("no_proxy_limitations_documented")
    return out
