"""Create draft pipeline entry."""

from __future__ import annotations

from app.authoring.schemas.draft import AuthoringDraft


def run_create_draft(draft: AuthoringDraft, save) -> AuthoringDraft:  # type: ignore[no-untyped-def]
    save(draft)
    return draft
