# Validation 02 — Post-Execution Completeness

## Identity

| Field | Value |
|---|---|
| Surface | `post-execution-completeness` |
| Type | Deterministic (field-presence + non-trivial check) |
| Triggered by | The critic, after a stage agent writes its artifact |
| Antonio Gulli patterns | Ch. 18 Guardrails/Safety, Ch. 19 Evaluation & Monitoring |
| Claude Code book chapters | Ch. 10 Failure Modes |

## Purpose

- **What this checks:** That the **top-level required fields** of a stage's output are present and non-trivial (not null, not `""`, not `{}`).
- **Why it exists:** Catches the most common producer failure: "I forgot to fill in `key_findings`" or "I left `summary` empty." Without this, the LLM-judge would catch it but the feedback would be vaguer.

## How it works

### Algorithm

Direct from `tools/validator.py:68-98`:

1. Parse artifact content as JSON.
2. Load schema via `tools/validator.py:load_schema`.
3. Iterate `schema["required"]`:
   - If `key not in data` → record as `missing`.
   - If `data[key] is None or data[key] == "" or data[key] == {}` → record as `empty`.
4. If `missing` or `empty` is non-empty → return `{"status": "fail", "error": "missing: [...]; empty: [...]"}`.
5. Else return `{"status": "pass", "error": ""}`.

### Source of truth

- `tools/validator.py:completeness_check` (L68–98) — implemented.
- `tools/validator.py:validate_artifact` (L101–168) — calls it for JSON stages; for TXT stages (only `01_ingest`), returns `{"status": "skip"}` (L124–126).

### Inputs

- `content: str` — the raw artifact file content
- `stage: str` — the stage id (e.g. `02_extract`)

### Outputs

- `{"status": "pass|fail|skip", "error": "..."}`

## Pass / fail criteria

- **Pass:** all `required` fields present and non-trivial.
- **Fail:** at least one `required` field missing or empty.
- **Skip:** `ext != "json"` (only `01_ingest/v1.txt` currently triggers this).
- **Threshold:** N/A (deterministic).
- **Retry semantics:** Fail → orchestrator retries the stage with feedback "missing: [...]" / "empty: [...]".

## How to invoke

### CLI

```bash
python -m tools.validator <input_id> <stage> <version> [ext] [option]
# e.g.
python -m tools.validator smokev200 02_extract 1 json
```

(Indirect — `validate_artifact` calls `completeness_check` internally. There is no standalone CLI for `completeness_check` alone; V2 may add one.)

### From an agent prompt

The critic calls `validate_artifact(input_id, stage, version, ext=ext, llm_judge_score=score)` per `agents/critic/AGENT.md` L21-40.

### From a smoke test

- `scripts/smoke_v2.py:208-222` — runs `validate_artifact` on every stage and asserts pass.
- `scripts/smoke_validator.py:46-56` — focused test: empty arrays must NOT fail completeness.

## Coverage

| Stage | Applies? | Notes |
|---|---|---|
| `00_research` | yes | Required: `topic`, `depth`, `queries`, `sources`, `synthesis` |
| `01_ingest` | skip (TXT) | The JSON variant of `01_ingest` (when `ext="json"`) is checked; TXT is `skip` per `tools/validator.py:124-126` |
| `02_extract` | yes | Required: `entities`, `facts`, `quotes` |
| `03_analyze` | yes | Required: `themes`, `gaps`, `contradictions` |
| `04_synthesize` | yes | Required: `summary`, `insights`, `narrative`, `diagrams`, `theses` |
| `05_format` | yes | Required: `summary`, `entities`, `facts`, `analysis`, `insights`, `references`, `diagrams`, `theses` |
| multi-option `options/<X>/` | yes | Same required fields as the stage root |

## Failure modes

- **JSON parse error** → `tools/validator.py:78` returns `{"status": "fail", "error": "not valid JSON: ..."}`. Surface verbatim.
- **Schema file missing** → `load_schema` raises `FileNotFoundError` → returned as `{"status": "fail", "error": "..."}`. Escalate to human (schema drift).
- **Empty arrays pass** → by design. "No quotes found" is a legitimate answer (`tools/validator.py:71-75`). Use the LLM-judge for "this array is too small" quality concerns.

## Refactor delta

- **Scope:** Small
- **Current state:** Works. `scripts/smoke_v2.py` and `scripts/smoke_validator.py` exercise it.
- **Target state:** Add a standalone CLI: `python -m tools.validator <input_id> <stage> <version> --check completeness`. Add `minItems` constraints to schemas for "this array must be non-empty" rules (currently enforced only by LLM-judge).
- **Concrete steps:**
  1. Add `--check {schema,completeness,llm_judge,all}` flag to `tools/validator.py:171-181` CLI.
  2. Add `minItems: 1` to `schemas/04_synthesize.json#insights` (currently no `minItems`; the LLM-judge is the only enforcement).
  3. Add `minItems: 2` to `schemas/04_synthesize.json#diagrams` and `#theses` (currently 0 — see `skills/04-synthesize.md` refactor delta).
  4. Update `scripts/smoke_v2.py` assertions to fail if `minItems` is violated.

## Source files (for traceability)

- `tools/validator.py:68-98` — `completeness_check` implementation
- `tools/validator.py:101-168` — `validate_artifact` (caller)
- `tools/validator.py:118-126` — TXT short-circuit
- `schemas/*.json` — source of `required` arrays
- `scripts/smoke_v2.py:208-222` — E2E exercise
- `scripts/smoke_validator.py:46-56` — focused exercise
