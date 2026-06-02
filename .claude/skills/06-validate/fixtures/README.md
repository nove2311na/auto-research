# Fixtures for 06-validate

The critic doesn't produce artifacts — it produces a `validation` block in `v<N>.meta.json`.

| File | Shape | Used by eval-case |
|---|---|---|
| `pass-meta.json` | meta with score=0.85, status=pass | V1 |
| `fail-schema-meta.json` | meta with checks.schema=fail | V2 |
| `fail-threshold-meta.json` | meta with score=0.5 | V3 |
| `tie-options.json` | 3 options with same LLM-judge score | V4 |
