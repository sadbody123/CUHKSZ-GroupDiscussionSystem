"""Runtime profile listing (API / UI)."""

from __future__ import annotations

from app.runtime.profile_resolver import list_resolved_profile_summaries, resolve_runtime_profile


class ProfileService:
    def list_profiles(self) -> list[dict]:
        return list_resolved_profile_summaries()

    def get_profile(self, profile_id: str) -> dict:
        p = resolve_runtime_profile(profile_id)
        return p.merged_dict()
