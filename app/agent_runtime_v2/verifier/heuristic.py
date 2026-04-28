"""Heuristic-first verifier implementation with multi-signal scoring.

Signals evaluated:
  - length:           reply length below policy threshold
  - topic_relevance:  keyword overlap ratio between topic terms and reply text
  - response_linkage: keyword overlap ratio between previous turn and reply text
  - stance_consistency: whether reply stance keywords align with expected role stance
  - repetition:       high n-gram overlap with the agent's own previous turns
"""

from __future__ import annotations

import re

from app.agent_runtime_v2.policy.quality_policy import QualityPolicy
from app.agent_runtime_v2.verifier.base import QualityVerifier, VerifierDecision
from app.runtime.enums import RoleType
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 1]


def _keyword_overlap_ratio(query_tokens: list[str], text_tokens: list[str]) -> float:
    if not query_tokens:
        return 1.0
    text_set = set(text_tokens)
    hits = sum(1 for t in query_tokens if t in text_set)
    return hits / len(query_tokens)


def _ngram_set(tokens: list[str], n: int = 3) -> set[str]:
    if len(tokens) < n:
        return set()
    return {"".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def _topic_keywords(session: SessionContext) -> list[str]:
    keywords: list[str] = []
    if session.topic_id:
        keywords.extend(_tokenize(str(session.topic_id)))
    if session.user_stance:
        keywords.extend(_tokenize(str(session.user_stance)))
    return keywords


_STANCE_MAP: dict[str, dict[str, list[str]]] = {
    RoleType.ALLY.value: {
        "aligned": [
            "agree", "support", "indeed", "furthermore", "reinforces",
            "bolsters", "aligns", "consistent with", "compelling",
            "strong point", "valid", "convincing",
        ],
        "opposed": [
            "disagree", "however", "nevertheless", "conversely", "but",
            "challenge", "counter", "refute", "opposing",
        ],
    },
    RoleType.OPPONENT.value: {
        "aligned": [
            "disagree", "challenge", "however", "but", "nevertheless",
            "conversely", "counter", "refute", "flawed", "opposing",
        ],
        "opposed": [
            "agree", "support", "indeed", "furthermore", "reinforces",
        ],
    },
}


def _stance_consistency_score(
    reply_tokens: list[str],
    role: str,
) -> float:
    stance_info = _STANCE_MAP.get(role)
    if not stance_info:
        return 1.0
    aligned_kw = stance_info["aligned"]
    opposed_kw = stance_info["opposed"]
    if not aligned_kw and not opposed_kw:
        return 1.0
    reply_lower = " ".join(reply_tokens)
    aligned_hits = sum(1 for kw in aligned_kw if kw in reply_lower)
    opposed_hits = sum(1 for kw in opposed_kw if kw in reply_lower)
    total = aligned_hits + opposed_hits
    if total == 0:
        return 1.0
    return aligned_hits / total


def _self_repetition_score(
    reply_tokens: list[str],
    session: SessionContext,
    current_role: str,
) -> float:
    own_prev_texts: list[str] = []
    for t in session.turns[-6:]:
        if t.speaker_role == current_role and t.text:
            own_prev_texts.append(t.text)
    if not own_prev_texts:
        return 0.0
    combined_prev = " ".join(own_prev_texts)
    prev_tokens = _tokenize(combined_prev)
    prev_ngrams = _ngram_set(prev_tokens, n=3)
    reply_ngrams = _ngram_set(reply_tokens, n=3)
    if not prev_ngrams or not reply_ngrams:
        return 0.0
    overlap = len(prev_ngrams & reply_ngrams)
    return overlap / max(len(reply_ngrams), 1)


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
        role = str(reply.role or "").lower().strip()
        reply_tokens = _tokenize(text)

        # 1. Length check
        if len(text) < int(policy.min_reply_length):
            flags.append("too_short")
        scores["length"] = float(len(text))

        # 2. Topic relevance via keyword overlap
        topic_kw = _topic_keywords(session)
        if topic_kw:
            topic_ratio = _keyword_overlap_ratio(topic_kw, reply_tokens)
            scores["topic_relevance"] = topic_ratio
            if topic_ratio < float(policy.topic_relevance_threshold):
                flags.append("weak_topic_relevance")
        else:
            scores["topic_relevance"] = 1.0

        # 3. Response linkage via keyword overlap
        linkage = 0.0
        if session.turns and len(session.turns) >= 2:
            prev_text = str(session.turns[-2].text or "").strip()
            if prev_text:
                prev_tokens = _tokenize(prev_text)
                linkage = _keyword_overlap_ratio(prev_tokens, reply_tokens)
        scores["response_linkage"] = linkage
        if linkage < float(policy.response_linkage_threshold) and len(session.turns) >= 2:
            flags.append("weak_response_link")

        # 4. Stance consistency
        stance_score = _stance_consistency_score(reply_tokens, role)
        scores["stance_consistency"] = stance_score
        if stance_score < 0.3 and role in (RoleType.ALLY.value, RoleType.OPPONENT.value):
            flags.append("inconsistent_stance")

        # 5. Self-repetition detection
        repetition = _self_repetition_score(reply_tokens, session, role)
        scores["self_repetition"] = repetition
        if repetition > 0.6:
            flags.append("excessive_self_repetition")

        # Decision: any quality flag → repair; multiple → interrupt
        if len(flags) >= 2 and bool(policy.enable_interrupt):
            decision = "interrupt"
        elif flags:
            decision = "repair"
        else:
            decision = "pass"
        return VerifierDecision(decision=decision, flags=flags, scores=scores)