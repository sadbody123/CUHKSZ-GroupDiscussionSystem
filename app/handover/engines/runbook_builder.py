"""Generate runbook text."""

from __future__ import annotations


def build_runbook_markdown(profile_id: str) -> str:
    return "\n".join(
        [
            f"# Final runbook ({profile_id})",
            "",
            "1. `python main.py validate-env`",
            f"2. `python main.py audit-release-readiness --profile-id {profile_id}`",
            "3. `python main.py run-api` (separate terminal)",
            "4. `python main.py run-ui`",
            "5. Optional: `python main.py verify-delivery --profile-id " + profile_id + "`",
            "",
        ]
    )
