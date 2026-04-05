# Roster templates and seat policies

`RosterTemplate` YAML defines seats, teams, and optional priorities for intro/summary ordering. `SeatPolicy` defaults are generated in `app/group_sim/engines/roster_resolver.py` (`default_seat_policies`).

Assessment templates `gd_assessment_4p_v1` / `gd_assessment_6p_v1` map to `gd_4p_assessment` / `gd_6p_assessment` via `app/group_sim/constants.py` when a session is created without an explicit roster.
