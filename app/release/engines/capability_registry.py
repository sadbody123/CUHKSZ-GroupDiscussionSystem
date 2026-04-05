"""Built-in capability inventory (aligned to repo modules)."""

from __future__ import annotations

from app.release.constants import (
    AREA_API,
    AREA_AUDIO,
    AREA_AUTHORING,
    AREA_CURRICULUM,
    AREA_EVAL,
    AREA_GROUP,
    AREA_INDEXING,
    AREA_LEARNER,
    AREA_MODES,
    AREA_OFFLINE,
    AREA_OPS,
    AREA_REVIEW,
    AREA_RUNTIME,
    AREA_SPEECH,
    AREA_UI,
    BETA,
    EXPERIMENTAL,
    STABLE,
)
from app.release.schemas.capability import CapabilityDescriptor

CAPABILITY_LIST: list[CapabilityDescriptor] = [
    CapabilityDescriptor(
        capability_id="offline_build",
        display_name="Offline snapshot build",
        area=AREA_OFFLINE,
        stability=STABLE,
        requires=[],
        related_artifact_kinds=["snapshot"],
        related_api_groups=[],
        notes=["datahub import → snapshot"],
    ),
    CapabilityDescriptor(
        capability_id="runtime_text_core",
        display_name="Text discussion runtime",
        area=AREA_RUNTIME,
        stability=STABLE,
        requires=[],
        related_api_groups=["/sessions"],
    ),
    CapabilityDescriptor(
        capability_id="api_mvp",
        display_name="FastAPI MVP",
        area=AREA_API,
        stability=STABLE,
        requires=["runtime_text_core"],
    ),
    CapabilityDescriptor(
        capability_id="ui_mvp",
        display_name="Streamlit UI MVP",
        area=AREA_UI,
        stability=STABLE,
        requires=["api_mvp"],
    ),
    CapabilityDescriptor(
        capability_id="eval_framework",
        display_name="Evaluation framework",
        area=AREA_EVAL,
        stability=STABLE,
        requires=["runtime_text_core"],
    ),
    CapabilityDescriptor(
        capability_id="runtime_profiles",
        display_name="Runtime profiles",
        area=AREA_RUNTIME,
        stability=STABLE,
        requires=[],
        related_api_groups=["/profiles"],
    ),
    CapabilityDescriptor(
        capability_id="hybrid_retrieval",
        display_name="Lexical / vector / hybrid retrieval",
        area=AREA_INDEXING,
        stability=BETA,
        requires=["runtime_text_core"],
    ),
    CapabilityDescriptor(
        capability_id="audio_practice",
        display_name="ASR / TTS / audio session",
        area=AREA_AUDIO,
        stability=BETA,
        requires=["runtime_text_core"],
        optional_requires=["api_mvp"],
    ),
    CapabilityDescriptor(
        capability_id="speech_proxy_feedback",
        display_name="Speech analysis & proxy metrics",
        area=AREA_SPEECH,
        stability=BETA,
        requires=["runtime_text_core"],
        optional_requires=["audio_practice"],
    ),
    CapabilityDescriptor(
        capability_id="learner_analytics",
        display_name="Learner profile & recommendations",
        area=AREA_LEARNER,
        stability=BETA,
        requires=["runtime_text_core"],
        related_api_groups=["/learners"],
    ),
    CapabilityDescriptor(
        capability_id="practice_modes",
        display_name="Modes / presets / drills / assessments",
        area=AREA_MODES,
        stability=BETA,
        requires=["runtime_text_core"],
        related_api_groups=["/modes"],
    ),
    CapabilityDescriptor(
        capability_id="group_simulation",
        display_name="Multi-seat group simulation",
        area=AREA_GROUP,
        stability=BETA,
        requires=["runtime_text_core", "practice_modes"],
    ),
    CapabilityDescriptor(
        capability_id="review_workspace",
        display_name="Review workspace & calibration",
        area=AREA_REVIEW,
        stability=BETA,
        requires=["runtime_text_core"],
        related_api_groups=["/review-packs"],
    ),
    CapabilityDescriptor(
        capability_id="curriculum_delivery",
        display_name="Curriculum packs & assignments",
        area=AREA_CURRICULUM,
        stability=BETA,
        requires=["runtime_text_core"],
        related_api_groups=["/curriculum-packs", "/assignments"],
    ),
    CapabilityDescriptor(
        capability_id="authoring_studio",
        display_name="Authoring & publication",
        area=AREA_AUTHORING,
        stability=EXPERIMENTAL,
        requires=["curriculum_delivery"],
        related_api_groups=["/authoring"],
    ),
    CapabilityDescriptor(
        capability_id="engineering_ops",
        display_name="Ops CLI, bundles, artifact registry",
        area=AREA_OPS,
        stability=STABLE,
        requires=[],
    ),
]


def all_capabilities() -> list[CapabilityDescriptor]:
    return list(CAPABILITY_LIST)


def get_capability(capability_id: str) -> CapabilityDescriptor | None:
    for c in CAPABILITY_LIST:
        if c.capability_id == capability_id:
            return c
    return None
