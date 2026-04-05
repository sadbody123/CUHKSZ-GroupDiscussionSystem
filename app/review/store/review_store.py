"""Review packs, human reviews, calibration, reviewed outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.review.schemas.calibration import CalibrationReport
from app.review.schemas.pack import ReviewPack
from app.review.schemas.report import HumanReview, ReviewedOutputArtifact

_SAFE = re.compile(r"^[\w.\-]+$")


class ReviewStore:
    def __init__(
        self,
        packs_dir: Path,
        submissions_dir: Path,
        calibration_dir: Path,
        reviewed_dir: Path,
    ) -> None:
        self._packs = packs_dir.resolve()
        self._subs = submissions_dir.resolve()
        self._cal = calibration_dir.resolve()
        self._out = reviewed_dir.resolve()
        for d in (self._packs, self._subs, self._cal, self._out):
            d.mkdir(parents=True, exist_ok=True)

    def save_review_pack(self, pack: ReviewPack) -> Path:
        if not _SAFE.match(pack.review_pack_id):
            raise ValueError("invalid review_pack_id")
        p = self._packs / f"{pack.review_pack_id}.json"
        p.write_text(json.dumps(pack.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_review_pack(self, review_pack_id: str) -> ReviewPack | None:
        p = self._packs / f"{review_pack_id}.json"
        if not p.is_file():
            return None
        return ReviewPack.model_validate_json(p.read_text(encoding="utf-8"))

    def list_review_packs(self) -> list[ReviewPack]:
        out: list[ReviewPack] = []
        for f in sorted(self._packs.glob("*.json")):
            try:
                out.append(ReviewPack.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out

    def save_human_review(self, review: HumanReview) -> Path:
        if not _SAFE.match(review.review_id):
            raise ValueError("invalid review_id")
        p = self._subs / f"{review.review_id}.json"
        p.write_text(json.dumps(review.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_human_review(self, review_id: str) -> HumanReview | None:
        p = self._subs / f"{review_id}.json"
        if not p.is_file():
            return None
        return HumanReview.model_validate_json(p.read_text(encoding="utf-8"))

    def list_human_reviews_for_pack(self, review_pack_id: str) -> list[HumanReview]:
        out: list[HumanReview] = []
        for f in sorted(self._subs.glob("*.json")):
            try:
                raw = json.loads(f.read_text(encoding="utf-8"))
                if raw.get("review_pack_id") == review_pack_id:
                    out.append(HumanReview.model_validate(raw))
            except Exception:
                continue
        return sorted(out, key=lambda r: r.created_at)

    def list_reviews_for_session(self, session_id: str) -> list[HumanReview]:
        packs = {p.review_pack_id: p for p in self.list_review_packs() if p.session_id == session_id}
        out: list[HumanReview] = []
        for f in sorted(self._subs.glob("*.json")):
            try:
                hr = HumanReview.model_validate_json(f.read_text(encoding="utf-8"))
                if hr.review_pack_id in packs:
                    out.append(hr)
            except Exception:
                continue
        return out

    def save_calibration_report(self, report: CalibrationReport) -> Path:
        key = f"{report.review_pack_id}_{report.review_id or 'noid'}.json"
        p = self._cal / key
        p.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_calibration_report(self, review_pack_id: str, review_id: str | None = None) -> CalibrationReport | None:
        key = f"{review_pack_id}_{review_id or 'noid'}.json"
        p = self._cal / key
        if p.is_file():
            return CalibrationReport.model_validate_json(p.read_text(encoding="utf-8"))
        # fallback: latest matching prefix
        candidates = sorted(self._cal.glob(f"{review_pack_id}_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        if candidates:
            return CalibrationReport.model_validate_json(candidates[0].read_text(encoding="utf-8"))
        return None

    def save_reviewed_output(self, artifact: ReviewedOutputArtifact) -> Path:
        name = f"{artifact.review_pack_id}_reviewed_feedback.json"
        p = self._out / name
        p.write_text(json.dumps(artifact.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_reviewed_output(self, review_pack_id: str) -> dict[str, Any] | None:
        p = self._out / f"{review_pack_id}_reviewed_feedback.json"
        if not p.is_file():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
