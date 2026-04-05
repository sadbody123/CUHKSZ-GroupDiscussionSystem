# Assignment completion and delivery reports

**Completion** uses session-linked artifacts (transcript, coach report, optional mode/speech/group IDs) with simple rule checks. Missing artifacts degrade gracefully.

**DeliverySummary** and **AssignmentReport** aggregate step status and learner coverage. Reports include **proxy_notes** reminding that speech, simulation, and learner analytics are training aids unless your institution adopts separate validated assessment.

Export JSON via CLI `export-assignment-report` or API `GET /assignments/{id}/report`.
