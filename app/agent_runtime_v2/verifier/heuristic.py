"""Heuristic-first verifier implementation."""

from __future__ import annotations

from app.agent_runtime_v2.policy.quality_policy import QualityPolicy
from app.agent_runtime_v2.verifier.base import QualityVerifier, VerifierDecision
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


def _topic_keyword(topic_id: str | None) -> str:
    if not topic_id:
        return ""
    return str(topic_id).replace("_", "-").split("-")[-1].strip().lower()


class HeuristicQualityVerifier(QualityVerifier):
    def verify(
        self,
        *,
        session: SessionContext,
        reply: AgentReply | None,
        policy: QualityPolicy,
    ) -> VerifierDecision:
        if reply is None:
            return VerifierDecision(decision="pass")

        flags: list[str] = []
        scores: dict = {}
        text = str(reply.text or "").strip()
        if len(text) < int(policy.min_reply_length):
            flags.append("too_short")
        scores["length"] = float(len(text))

        topic_kw = _topic_keyword(session.topic_id)
        topic_hit = float(1.0 if (topic_kw and topic_kw in text.lower()) else 0.0)
        scores["topic_relevance"] = topic_hit
        if topic_kw and topic_hit < float(policy.topic_relevance_threshold):
            flags.append("weak_topic_relevance")

        linkage = 1.0
        if session.turns and len(session.turns) >= 2:
            prev = str(session.turns[-2].text or "").strip().lower()
            key = prev[:20] if prev else ""
            linkage = float(1.0 if (key and key in text.lower()) else 0.0)
        scores["response_linkage"] = linkage
        if linkage < float(policy.response_linkage_threshold):
            flags.append("weak_response_link")

        decision = "pass" if not flags else "repair"
        return VerifierDecision(decision=decision, flags=flags, scores=scores)
