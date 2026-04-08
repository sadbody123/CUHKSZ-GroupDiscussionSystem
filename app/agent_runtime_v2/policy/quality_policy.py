"""Policy-first quality configuration for discussion graph."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.runtime.profile_resolver import resolve_runtime_profile


class QualityPolicy(BaseModel):
    policy_id: str = "quality_default_v1"
    min_reply_length: int = 40
    topic_relevance_threshold: float = 0.5
    response_linkage_threshold: float = 0.5
    max_repairs: int = 1
    interrupt_after_max_repairs: bool = True
    enable_interrupt: bool = True
    per_role_overrides: dict[str, dict] = Field(default_factory=dict)

    def for_role(self, role: str | None) -> "QualityPolicy":
        r = str(role or "").strip().lower()
        if not r:
            return self
        override = self.per_role_overrides.get(r)
        if not isinstance(override, dict):
            return self
        return self.model_copy(update=override)


class QualityPolicyResolver:
    """Resolve policy from runtime profile metadata."""

    def resolve(self, runtime_profile_id: str, *, role: str | None = None) -> QualityPolicy:
        prof = resolve_runtime_profile(runtime_profile_id)
        raw = {}
        if isinstance(prof.metadata, dict):
            raw = dict(prof.metadata.get("quality_policy") or {})
        p = QualityPolicy.model_validate(raw or {})
        return p.for_role(role)
