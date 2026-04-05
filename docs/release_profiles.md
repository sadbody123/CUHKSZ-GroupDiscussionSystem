# Release profiles

Profiles are YAML files in `app/release/profiles/`.

| Profile id | Intent |
|------------|--------|
| `v1_minimal` | Core text practice, basic API/UI, minimal surface area for smoke. |
| `v1_demo` | Showcase subset: learner, modes, group, review, curriculum; optional audio/speech as experimental. |
| `v1_full_local` | Local “all features visible”; experimental flags may be enabled. |

## Loading

- **Default**: `ACTIVE_RELEASE_PROFILE` in `app/ops/settings.py` (env).
- **CLI**: `--profile-id` on release commands.
- **API**: `GET /system/release-profile?profile_id=...`

## Policies

Each profile may define:

- `enabled_capabilities` / `disabled_capabilities` / `experimental_capabilities`
- `ui_visibility_policy` / `api_visibility_policy` for **visibility** (not authorization).

See `app/release/schemas/profile.py` for the full schema.
