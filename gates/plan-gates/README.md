# Plan gates

## `plan_review_gate.py` (V2 follow-up)
- **When:** between orchestrator's handoff plan and the first stage dispatch.
- **Checks:** plan has steps + risks + test strategy + rollback-if-needed.
- **On fail:** revise plan; orchestrator loops.

Not yet implemented in V1.
