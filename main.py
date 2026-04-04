#!/usr/bin/env python3
"""CLI entry: `python main.py <command> ...`"""

from __future__ import annotations

from app.offline_build.cli.commands import app

if __name__ == "__main__":
    app()
