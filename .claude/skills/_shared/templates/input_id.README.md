# Deriving `input_id`

Every pipeline run has an 8-hex `input_id` derived from the input_ref.

```python
import hashlib

def input_id_for(input_ref: str) -> str:
    """8-hex from sha1 of the input_ref. Same input_ref -> same input_id."""
    return hashlib.sha1(input_ref.encode("utf-8")).hexdigest()[:8]
```

## Examples

| input_ref | input_id |
|---|---|
| `topic: "Quantum error correction 2026"` | `8f3a2b1c` |
| `path: inputs/inbox/qec.pdf` | (depends on filename) |
| `url: https://example.com/qec-2026` | (depends on URL) |

## Where it appears

- `outputs/<input_id>/<stage>/v<N>.<ext>` — file path
- `prd.json#current_input_id` — orchestrator's state
- `manifest.json#stages` — audit trail
- `meta.input_id` — every artifact's meta
- `hcom send --name <sender> "@research-pipeline-claude-N <stage>: <input_id>; input=<path>"` — handoff

## Invariant

Two pipeline runs with the same `input_ref` produce the same `input_id`. This means the inbox/processed/ mechanism (per `tools/fetch_input.py`) can dedupe.
