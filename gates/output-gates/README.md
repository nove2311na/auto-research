# Output gates

## `json_schema_gate.py`
- **When:** every Write to `outputs/<id>/<stage>/v<N>.<ext>`.
- **What:** Draft-7 schema check.
- **On fail:** BLOCK the write; orchestrator retries the stage.

## `llm_judge_gate.py`
- **When:** after the critic records a score in meta.
- **What:** threshold check (pipeline.json#threshold).
- **On fail:** return fail status; orchestrator retries.

## `manifest_consistency_gate.py`
- **When:** before `manifest.finalize()`.
- **What:** winner matches options; no orphan meta files.
- **On fail:** refuse finalize; orchestrator re-picks.
