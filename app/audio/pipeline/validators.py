"""Upload validation."""

from __future__ import annotations


def validate_upload_size(size: int, max_bytes: int) -> None:
    if size > max_bytes:
        raise ValueError(f"audio too large: {size} bytes (max {max_bytes})")
