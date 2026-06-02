# Release gates

## `manifest_finalize_gate.py`
- **When:** formatter's last step (before `manifest.finalize`).
- **Checks:** all 6 stages have `validation.status=pass`; manifest.completed_at not set.
- **On fail:** refuse finalize; orchestrator re-runs the failing stage.

Already partially implemented as `tools.manifest.finalize` invariants.
