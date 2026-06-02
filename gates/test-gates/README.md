# Test gates

## `smoke_test_gate.py`
- **When:** before finalize on every input_id.
- **Checks:** `scripts/smoke_v2.py` would pass on the same schema contracts.
- **On fail:** refuse finalize.

Not yet implemented in V1; the smoke script is run manually.
