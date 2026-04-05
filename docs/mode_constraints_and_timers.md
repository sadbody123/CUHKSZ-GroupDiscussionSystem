# Mode constraints and timers

## Constraints

`app/modes/engines/constraint_engine.py` evaluates **soft** rules on user text (e.g. long-turn word count) and appends events to `SessionContext.mode_state["constraint_events"]`. This reuses the existing session store and state machine; it does not fork a second runtime.

## Timers

`app/modes/engines/timer_policy.py` computes a **deterministic** `timer_state` dict from:

- session metadata timestamps, and  
- mode `timer_policy` / assessment template phase budgets.

CLI and API consumers can refresh `GET /sessions/{id}/mode-status` or read embedded `timer_state` on `GET /sessions/{id}` — no wall-clock daemon is required.
