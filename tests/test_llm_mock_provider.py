"""Mock LLM provider (offline, deterministic)."""

from __future__ import annotations

from app.runtime.llm.providers.mock_provider import MockProvider
from app.runtime.schemas.llm import GenerationRequest, LLMMessage


def test_mock_deterministic_same_input():
    p = MockProvider()
    req = GenerationRequest(
        provider_name="mock",
        model="m1",
        messages=[LLMMessage(role="user", content="hello world")],
        metadata={"role": "ally"},
    )
    a = p.generate(req)
    b = p.generate(req)
    assert a.text == b.text
    assert "ally" in a.text.lower() or "MOCK" in a.text


def test_mock_role_styles_differ():
    p = MockProvider()
    base = GenerationRequest(
        provider_name="mock",
        messages=[LLMMessage(role="user", content="same")],
        metadata={"role": "moderator"},
    )
    t_mod = p.generate(base).text
    t_opp = p.generate(
        GenerationRequest(provider_name="mock", messages=base.messages, metadata={"role": "opponent"})
    ).text
    assert t_mod != t_opp
