"""Human-readable summaries of context dicts."""

from __future__ import annotations


def summarize_topic_card(card: dict | None) -> str:
    if not card:
        return "(none)"
    topic = card.get("topic") or card.get("title") or ""
    summ = card.get("summary") or ""
    return f"Topic: {topic}\nSummary: {summ}"


def summarize_pedagogy(items: list[dict], *, max_items: int = 6) -> str:
    if not items:
        return "(none)"
    lines: list[str] = []
    for p in items[:max_items]:
        iid = p.get("item_id", "?")
        it = p.get("item_type", "?")
        c = str(p.get("content", ""))[:400]
        lines.append(f"- [{it} {iid}] {c}")
    return "\n".join(lines)


def summarize_evidence(items: list[dict], *, max_items: int = 6) -> str:
    if not items:
        return "(none)"
    lines: list[str] = []
    for e in items[:max_items]:
        eid = e.get("evidence_id", "?")
        t = str(e.get("text", ""))[:320]
        lines.append(f"- [{eid}] {t}")
    return "\n".join(lines)
