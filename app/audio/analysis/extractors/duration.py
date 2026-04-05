"""Duration helpers."""

from __future__ import annotations


def ms_from_frames(frame_count: int, sample_rate: int) -> int:
    if sample_rate <= 0:
        return 0
    return int(1000 * frame_count / sample_rate)
