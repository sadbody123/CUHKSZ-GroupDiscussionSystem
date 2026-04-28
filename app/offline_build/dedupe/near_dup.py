"""Near-duplicate detection via SimHash fingerprinting.

Uses standard-library hashlib (no external deps) to compute 128-bit
SimHash fingerprints. Documents whose Hamming distance falls below
a configurable threshold are clustered, and only the first document
in each cluster is retained.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from app.schemas.normalized_doc import NormalizedDocument


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in text.split() if w]


def _compute_simhash(text: str, bits: int = 128) -> int:
    tokens = _tokenize(text)
    if not tokens:
        return 0
    v = [0] * bits
    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        for i in range(bits):
            v[i] += 1 if (h >> (i % 128)) & 1 else -1
    result = 0
    for i in range(bits):
        if v[i] >= 0:
            result |= 1 << i
    return result


def _hamming_distance(a: int, b: int) -> int:
    return (a ^ b).bit_count()


@dataclass
class NearDupDetector:
    """SimHash-based near-duplicate document detector."""

    hash_bits: int = 128
    similarity_threshold: float = 0.85

    def find_near_duplicates(
        self, docs: list[NormalizedDocument]
    ) -> list[list[str]]:
        """Return clusters of near-duplicate document IDs.

        Each inner list represents one cluster; the first element is the
        canonical document to keep, subsequent elements are candidates to drop.
        """
        doc_map = {d.doc_id: d for d in docs if d.doc_id and d.clean_text}
        if len(doc_map) < 2:
            return []

        hashes: dict[str, int] = {
            did: _compute_simhash(d.clean_text, self.hash_bits)
            for did, d in doc_map.items()
        }

        ids = list(doc_map.keys())
        clusters: list[list[str]] = []
        assigned: set[str] = set()

        for i, did_a in enumerate(ids):
            if did_a in assigned:
                continue
            cluster = [did_a]
            for did_b in ids[i + 1:]:
                if did_b in assigned:
                    continue
                ham = _hamming_distance(hashes[did_a], hashes[did_b])
                sim = 1.0 - ham / self.hash_bits
                if sim >= self.similarity_threshold:
                    cluster.append(did_b)
                    assigned.add(did_b)
            if len(cluster) > 1:
                clusters.append(cluster)
            assigned.add(did_a)

        return clusters