"""Release YAML validators."""

from __future__ import annotations


def validate_profile_dict(raw: dict) -> None:
    if not raw.get("profile_id"):
        raise ValueError("profile_id required")
