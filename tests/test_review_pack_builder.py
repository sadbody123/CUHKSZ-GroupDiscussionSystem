from __future__ import annotations

from pathlib import Path

from app.review.engines.pack_builder import build_review_pack
from app.runtime.schemas.session import SessionContext


def test_build_review_pack_minimal(tmp_path: Path) -> None:
    ctx = SessionContext(
        session_id="s1",
        topic_id="t1",
        snapshot_dir=str(tmp_path),
        coach_report={"strengths": ["a"], "risks": ["b"], "feedback_packet": {}},
    )
    pack = build_review_pack(
        ctx,
        speech_report_dir=tmp_path / "sp",
        mode_reports_dir=tmp_path / "m",
        group_reports_dir=tmp_path / "g",
    )
    assert pack.session_id == "s1"
    assert "session" in pack.included_artifacts
