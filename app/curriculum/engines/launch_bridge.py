"""Map pack step to session launch parameters."""

from __future__ import annotations

from typing import Any

from app.curriculum.schemas.pack import CurriculumPack, CurriculumPackStep


def find_step(pack: CurriculumPack, pack_step_id: str) -> CurriculumPackStep | None:
    for st in pack.steps:
        if st.step_id == pack_step_id:
            return st
    return None


def build_session_launch_kwargs(
    pack: CurriculumPack,
    pack_step_id: str,
    *,
    learner_id: str | None,
    snapshot_id: str,
    provider_name: str = "mock",
) -> dict[str, Any]:
    st = find_step(pack, pack_step_id)
    if not st:
        raise ValueError(f"pack step not found: {pack_step_id}")
    topic = st.topic_id or (pack.linked_topic_ids[0] if pack.linked_topic_ids else "tc-campus-ai")
    audio = (st.learner_mode or "").lower() in ("audio", "mixed")
    return {
        "snapshot_id": snapshot_id,
        "topic_id": topic,
        "user_stance": None,
        "provider_name": provider_name,
        "runtime_profile_id": st.runtime_profile_id or "default",
        "learner_id": learner_id,
        "mode_id": st.mode_id,
        "preset_id": st.preset_id,
        "drill_id": st.drill_id,
        "assessment_template_id": st.assessment_template_id,
        "roster_template_id": st.roster_template_id,
        "source": "curriculum",
        "curriculum_pack_id": pack.pack_id,
        "assignment_context": {
            "focus_skills": st.focus_skills,
            "required_pedagogy_item_ids": st.required_pedagogy_item_ids,
            "step_objective": st.objective,
        },
        "audio_enabled": audio,
    }
