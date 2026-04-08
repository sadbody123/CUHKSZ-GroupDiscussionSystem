"""Export FastAPI OpenAPI schema into frontend generated folder."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    frontend_dir = Path(__file__).resolve().parents[1]
    repo_root = frontend_dir.parent
    sys.path.insert(0, str(repo_root))

    from app.api.main import create_app  # noqa: PLC0415

    out_dir = frontend_dir / "src" / "api" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "openapi.schema.json"

    app = create_app()
    schema = app.openapi()
    out_file.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OpenAPI schema exported to: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
