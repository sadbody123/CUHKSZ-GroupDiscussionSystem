"""Near-duplicate detection — placeholder for future fuzzy / embedding methods."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NearDupDetector:
    """
    Minimal interface stub.

    TODO: integrate simhash/minhash or embedding similarity when required.
    """

    def find_near_duplicates(self, doc_ids: list[str]) -> list[tuple[str, str]]:
        """Return pairs of possibly duplicate doc ids (not used in phase 1)."""
        return []
