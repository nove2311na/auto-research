# Validation 01 — Pre-Execution Schema

## Identity

| Field | Value |
|---|---|
| Surface | `pre-execution-schema` |
| Type | Deterministic (JSON Schema Draft-7) |
| Triggered by | Stage agent before writing its artifact (currently manual; see Refactor delta) |
| Antonio Gulli patterns | Ch. 18 Guardrails/Safety, Ch. 19 Evaluation & Monitoring |
| Claude Code book chapters | Ch. 2 Permission Architecture, Ch. 10 Failure Modes |

## Purpose

- **What this checks:** That the **upstream artifact** a stage agent is about to consume is well-formed against the upstream stage's schema before the agent invests in producing a downstream artifact.
- **Why it exists:** Catches "garbage in, garbage out" early. A 02_extract that reads a malformed 01_ingest will produce a malformed 02_extract and waste a critic cycle.

## How it works

### Algorithm

1. Read upstream artifact at `outputs/<input_id>/<prev_stage>/v1.<ext>`.
2. For JSON ext: parse + validate against `schemas/<prev_stage>.json` via `jsonschema.Draft7Validator` (same code path as `tools/validator.py:46-65`).
3. For TXT ext (`01_ingest`): assert non-empty + UTF-8 decodable.
4. For multi-option (`02_extract/options/<X>/v1.json`): check **all** options, not just one.
5. Return `pass` / `fail` + the first 5 schema errors (same concise format as `tools/validator.py:60-64`).

### Source of truth (planned)

- `tools/validate_stage.py` (V2) — a per-stage driver that calls `validate_artifact` on the upstream artifact first.
- Reuses `tools/validator.py:load_schema` and `tools/validator.py:schema_check` unchanged.

### Inputs

- `input_id`, `stage` (the downstream stage about to run)

### Outputs

- `{"status": "pass|fail", "checks": {"upstream_schema": {...}}, "feedback": "..."}`

## Pass / fail criteria

- **Pass:** upstream artifact exists, parses, and validates against its schema (or is non-empty UTF-8 for TXT).
- **Fail:** upstream missing, parse error, or schema violation.
- **Threshold:** N/A (deterministic).
- **Retry semantics:** If fail, the orchestrator's handoff should NOT proceed to the downstream stage. Re-send the upstream stage with feedback (the schema error), or escalate to human.

## How to invoke

### CLI (planned for V2)

```bash
python -m tools.validate_stage <input_id> <stage> --preflight
```

### From an agent prompt (V1 — manual)

The stage agent should add a step to its process:

```python
# In skills/02-extract.md step 1 (deterministic)
from tools.validator import schema_check
content = read_artifact(input_id, "01_ingest", 1, ext="txt")  # or json
# Note: schema_check expects JSON, so for TXT this is text-content validation only
```

### From a smoke test

Planned: `scripts/smoke_preflight.py` (V2) — feeds a known-good + a known-bad upstream, asserts the preflight check distinguishes them.

## Coverage

| Stage | Upstream | Pre-execution applies? | Notes |
|---|---|---|---|
| `00_research` | `input_ref` (file/URL/topic) | partial | Validate that `input_ref` exists / URL is well-formed; do NOT preflight on topic strings |
| `01_ingest` | `00_research/v1.json` | yes | If `00_research` ran, validate dossier JSON before merging |
| `02_extract` | `01_ingest/v1.txt` | partial | TXT (not JSON) — only non-empty UTF-8 check |
| `03_analyze` | `02_extract/v1.json` (critic's winner) | yes | Validate the extract output before analyzing |
| `04_synthesize` | `03_analyze/v1.json` | yes | Same |
| `05_format` | `04_synthesize/v1.json` | yes | Same |

## Failure modes

- **Upstream missing** → `FileNotFoundError`. Surface to orchestrator; do not synthesize a default upstream.
- **Schema file missing** → BLOCK. Indicates a drift between `pipeline.json` and `schemas/`; escalate to human (matches `agents/critic/AGENT.md` "Failure modes" L62).
- **JSON parse error** → surface verbatim; do not retry (the upstream is broken at a deterministic level).

## Refactor delta

- **Scope:** Medium
- **Current state:** No pre-execution check exists. Stage agents implicitly trust their upstream. The critic catches the downstream artifact failure but not the root cause.
- **Target state:** A `tools/validate_stage.py` driver + a documented preflight step in each skill spec.
- **Concrete steps:**
  1. Author `tools/validate_stage.py` with `--preflight` mode.
  2. Add a numbered step to each `skills/NN-*.md` Process section: "**(deterministic)** Pre-flight upstream via `validate_stage --preflight`. Abort on fail."
  3. Add `scripts/smoke_preflight.py` to exercise it on a known-good + known-bad case.
  4. Update the orchestrator's retry logic to prefer preflight-fail feedback over post-execution fail feedback (saves a critic cycle).

## Source files (for traceability)

- `tools/validator.py:46-65` — `schema_check` (reused unchanged)
- `tools/validator.py:37-43` — `load_schema` (reused unchanged)
- `schemas/*.json` — the schema being validated against
- `AGENTS.md` invariant #2 — "Every artifact has a sibling `.meta.json`" (analogous invariant for upstream)
