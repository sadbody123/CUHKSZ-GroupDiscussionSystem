"""Verifier interfaces for quality decisions."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.agent_runtime_v2.policy.quality_policy import QualityPolicy
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


class VerifierDecision(BaseModel):
    decision: str  # pass | repair | interrupt
    flags: list[str] = Field(default_factory=list)
    scores: dict = Field(default_factory=dict)
    reason: str | None = None


class QualityVerifier:
    """Extension point for heuristic/LLM hybrid quality verification."""

    def verify(
        self,
        *,
        session: SessionContext,
        reply: AgentReply | None,
        policy: QualityPolicy,
    ) -> VerifierDecision:
        raise NotImplementedError
