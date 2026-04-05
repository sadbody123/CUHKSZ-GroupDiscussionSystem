"""Application version from package metadata.

Version is defined in ``pyproject.toml`` (``[project].version``). ``GET /health`` and CLI use this string.
"""

from __future__ import annotations


def get_app_version() -> str:
    try:
        from importlib.metadata import version

        return version("cuhksz-group-discussion-system")
    except Exception:
        return "0.1.0"
