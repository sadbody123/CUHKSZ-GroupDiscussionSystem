"""Bootstrap snapshot and start FastAPI backend for Playwright real E2E."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import uvicorn


def main() -> int:
    frontend_dir = Path(__file__).resolve().parents[1]
    repo_root = frontend_dir.parent
    subprocess.check_call([sys.executable, "main.py", "bootstrap-dev-snapshot"], cwd=repo_root)
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=8000, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
