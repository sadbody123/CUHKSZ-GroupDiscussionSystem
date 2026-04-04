"""Deterministic offline mock LLM (no network)."""

from __future__ import annotations

import hashlib
import json

from app.runtime.llm.base import BaseLLMProvider
from app.runtime.schemas.llm import GenerationRequest, GenerationResponse


class MockProvider(BaseLLMProvider):
    name = "mock"

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        role = str(request.metadata.get("role", "assistant")).lower()
        blob = json.dumps(
            {"messages": [m.model_dump() for m in request.messages], "model": request.model},
            sort_keys=True,
        )
        h = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
        style = {
            "moderator": "Brief facilitator note",
            "ally": "Supportive follow-up",
            "opponent": "Respectful challenge",
            "coach": "Formative feedback summary",
            "user": "Reflection",
        }.get(role, "Reply")
        last = request.messages[-1].content if request.messages else ""
        snippet = last.replace("\n", " ")[:120]
        text = f"[MOCK::{role}::{h}] {style}. Context tail: {snippet}"
        return GenerationResponse(
            provider_name=self.name,
            model=request.model or "mock-1",
            text=text,
            raw={"hash": h},
            metadata={"role": role},
        )
