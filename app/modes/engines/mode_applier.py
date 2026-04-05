"""Apply mode/preset/drill/template to a new SessionContext."""

from __future__ import annotations

from typing import Any

from app.modes.constants import SIMULATION_NOTE
from app.modes.engines.preset_resolver import effective_runtime_profile, merged_constraint_policy
from app.modes.engines.timer_policy import compute_timer_state
from app.modes.loaders.yaml_loader import get_mode_registry
from app.modes.loaders.validators import default_mode_id
from app.runtime.schemas.session import SessionContext


def apply_mode_context(
    ctx: SessionContext,
    *,
    mode_id: str | None,
    preset_id: str | None,
    drill_id: str | None,
    assessment_template_id: str | None,
) -> SessionContext:
    reg = get_mode_registry()
    mid = mode_id or default_mode_id()
    mode = reg.get_mode(mid)
    if not mode:
        mid = default_mode_id()
        mode = reg.get_mode(mid)
    preset = reg.get_preset(preset_id) if preset_id else None
    if preset and preset.mode_id != mid:
        # align to preset's mode if consistent
        om = reg.get_mode(preset.mode_id)
        if om:
            mid = preset.mode_id
            mode = om
    drill = reg.get_drill(drill_id) if drill_id else None
    if drill and drill.suggested_mode_id and drill.suggested_mode_id != mid:
        mm = reg.get_mode(drill.suggested_mode_id)
        if mm:
            mid = drill.suggested_mode_id
            mode = mm
    template = reg.get_template(assessment_template_id) if assessment_template_id else None

    ctx.mode_id = mid
    ctx.preset_id = preset_id
    ctx.drill_id = drill_id
    ctx.assessment_template_id = assessment_template_id

    mcp = merged_constraint_policy(mode, preset) if mode else {}
    ctx.runtime_profile_id = effective_runtime_profile(mode, preset, ctx.runtime_profile_id) if mode else ctx.runtime_profile_id
    if mode and mode.default_audio_enabled is True:
        ctx.audio_enabled = True

    ms: dict[str, Any] = {
        "effective_constraint_policy": mcp,
        "simulation_note": SIMULATION_NOTE if (mode and mode.mode_type == "assessment") or template else None,
    }
    if drill:
        ms["drill_objective"] = drill.objective
        ms["drill_success_criteria"] = drill.success_criteria
        ms["drill_prompts"] = drill.prompt_instructions
    if template:
        ms["assessment_template"] = template.template_id
        ms["simulation_disclaimer"] = (template.metadata or {}).get("disclaimer") or SIMULATION_NOTE

    ctx.mode_state = {**(ctx.mode_state or {}), **ms}
    ctx.timer_state = compute_timer_state(ctx, mode=mode, template=template)
    return ctx
