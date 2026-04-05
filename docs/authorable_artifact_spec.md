# Authorable artifact spec (Phase 16)

Supported `artifact_type` values align with `app/authoring/constants.py`:

| Type | Builtin source | Custom publish location |
|------|----------------|-------------------------|
| `topic_card` | Snapshot topic cards (read-only) | `authoring/published/artifacts/topic_cards/` |
| `pedagogy_item` | Pedagogy KB in snapshot | `.../pedagogy_items/` |
| `drill_spec` | Mode registry drills | `.../drills/` |
| `curriculum_pack` | `app/curriculum/packs/*.yaml` | `CURRICULUM_CUSTOM_PACK_DIR` JSON via `PackStore` |
| `scenario_preset` | Mode presets | `.../presets/` |
| `assessment_template` | Assessment templates | `.../assessment_templates/` |
| `roster_template` | Group sim roster YAML | `.../roster_templates/` |
| `runtime_profile` | `app/runtime/profiles/*.yaml` | `storage/authoring/published/runtime_profiles/*.yaml` |

**Rules**

- Custom publications must use **new** ids where a collision with built-in stems would imply override (curriculum `pack_id`, runtime `profile_id`, etc.).
- `AuthorableArtifactRef` records `source_type`: `builtin`, `custom_published`, `derived`, etc., plus optional `derivative_of` for lineage.
