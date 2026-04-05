# Assessment simulation (practice only)

**Assessment templates** (e.g. `gd_assessment_4p_v1`) describe timed *practice* phases for a simulated group discussion. They are **not** a formal examination, proctored test, or certified score.

- API responses and UI copy include a **simulation disclaimer** (`SIMULATION_NOTE` in `app/modes/constants.py`).
- **Soft timers** are derived from session `created_at` plus template budgets (`app/modes/engines/timer_policy.py`); there is no background invigilation or real-time sync.
- Combine `mode_id=assessment_simulation`, optional `preset_id` (e.g. `assessment_4p`), and `assessment_template_id` when creating a session.
