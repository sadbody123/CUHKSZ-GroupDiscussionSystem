# Multi-seat group simulation (Phase 13)

This project simulates **named seats and teams** with **one real learner** and **multiple AI participants**. It does **not** provide multiplayer networking or concurrent human users.

- Configuration lives under `app/group_sim/roster_templates/` as YAML.
- Runtime state is stored on `SessionContext` (`participants`, `teams`, `user_participant_id`, …).
- Turn order uses `app/group_sim/engines/turn_allocator.py` when `ENABLE_GROUP_SIM` is on and a roster is present.
