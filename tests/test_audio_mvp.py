"""Phase 9 audio MVP unit tests (mock-only)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.audio.pipeline.audio_store import AudioStore
from app.audio.providers.asr.mock_asr import MockASRProvider
from app.audio.providers.tts.mock_tts import MockTTSProvider
from app.audio.schemas.asr import TranscriptionRequest
from app.audio.schemas.tts import SynthesisRequest


def test_mock_asr_manifest_by_filename(tmp_path: Path) -> None:
    man = tmp_path / "m.json"
    man.write_text('{"hello.wav": "fixed text"}', encoding="utf-8")
    p = MockASRProvider(manifest_path=man)
    r = p.transcribe(TranscriptionRequest(provider_name="mock_asr", file_path=str(tmp_path / "hello.wav")))
    assert r.text == "fixed text"


def test_mock_tts_deterministic() -> None:
    p = MockTTSProvider()
    a = p.synthesize(SynthesisRequest(provider_name="mock_tts", text="hi", role="ally"))
    b = p.synthesize(SynthesisRequest(provider_name="mock_tts", text="hi", role="ally"))
    assert a.audio_bytes == b.audio_bytes
    assert a.mime_type == "audio/wav"


def test_audio_store_roundtrip(tmp_path: Path) -> None:
    st = AudioStore(tmp_path)
    rec = st.save_bytes(
        session_id="s1",
        data=b"abc",
        file_name="x.wav",
        asset_kind="user_upload",
        mime_type="audio/wav",
        provider_name="mock_asr",
    )
    got = st.read_bytes(rec.asset_id)
    assert got is not None
    data, r2 = got
    assert data == b"abc"
    assert r2.asset_id == rec.asset_id
