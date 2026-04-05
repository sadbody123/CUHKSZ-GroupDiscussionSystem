# Participant memory and turn allocation

`participant_memory.py` tracks lightweight per-seat facts (intro/summary completion, recent turn ids). `turn_allocator.py` chooses the next **runtime role** (`ally` / `opponent` / `user`) plus a **participant identity** for prompts and transcript rows.

Legacy sessions without `participants` continue to use `SessionStateMachine.peek_next_role`.
