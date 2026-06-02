# Template — Validation Spec

> **Use this template for every `validation/NN-<surface>.md` file in `.docs/agentic/validation/`.**
> Sections marked `[required]` must be present. Sections marked `[recommended]` may be omitted only with justification. Sections marked `[optional]` are at author discretion.

## Identity `[required]`

| Field | Value |
|---|---|
| Surface | (e.g. `pre-execution-schema`, `llm-judge`, `drift-detection`) |
| Type | (deterministic / LLM-judge / hybrid) |
| Triggered by | (which event causes this check to run) |
| Antonio Gulli patterns | (Ch. 19 Evaluation & Monitoring, Ch. 12 Exception Handling, Ch. 14 RAG, etc.) |

## Purpose `[required]`

- **What this checks:** (1-2 sentences)
- **Why it exists:** (1 sentence — what failure it prevents)

## How it works `[required]`

### Algorithm
- (numbered steps; for deterministic checks, this is the exact code; for LLM-judge, this is the prompt template)

### Source of truth
- (cite the runtime implementation file with line numbers; e.g. `tools/validator.py:46-65`)

### Inputs
- (what artifact / state this check consumes)

### Outputs
- (what it produces: `pass` / `fail` / score / feedback)

## Pass / fail criteria `[required]`

- **Pass:** (condition for pass)
- **Fail:** (condition for fail)
- **Threshold:** (e.g. `pipeline.json` → `critic.llm_judge_threshold` = 0.7)
- **Retry semantics:** (what happens on fail: retry with feedback / halt / human escalation)

## How to invoke `[required]`

### CLI
```bash
python -m tools.validator <input_id> <stage> <version> [ext] [option]
```

### From an agent prompt
- (the hcom message that triggers this check)

### From a smoke test
- (the `scripts/smoke_*.py` file that exercises this check)

## Coverage `[required]`

| Stage | Check applies? | Notes |
|---|---|---|
| `00_research` | yes | (e.g. JSON schema check) |
| `01_ingest` | partial | (e.g. `ext="txt"` → schema+completeness are `skip`) |
| `02_extract` | yes | (per-option, critic picks winner) |
| ... | ... | ... |

## Failure modes `[recommended]`

- (what this check does on its own failure: e.g. schema file missing → BLOCK, JSON parse error → surface, LLM-judge tie → tiebreak on schema+completeness, retries exhausted → halt)

## Refactor delta `[required]`

- **Scope:** (Small / Medium / Large)
- **Current state:** (1-2 sentences — what exists today)
- **Target state:** (1-2 sentences — what the post-refactor shape is)
- **Concrete steps:**
  1. ...
  2. ...

## Source files (for traceability)

- `tools/validator.py` — runtime validator
- `tools/manifest.py` — manifest helper (is_done, record_attempt, finalize)
- `scripts/smoke_v2.py` — full-pipeline E2E smoke
- `scripts/smoke_validator.py` — focused validator smoke
- (etc.)

---

**Authoring tips:**
- **Cite line numbers** for every code reference. The user values precision.
- **Distinguish deterministic from LLM-judge** clearly. The critic's LLM-judge is the only non-deterministic check (see `tools/validator.py:128-137`).
- **Threshold source must be cited.** Default is `pipeline.json` → `critic.llm_judge_threshold` (default 0.7).
- **Smoke tests should be <5s and network-free** (per `.claude/rules/python.md` "Testing" section).
- **`ext="txt"` short-circuit** at `tools/validator.py:118-126` is important — schema+completeness are `skip` for `01_ingest/v1.txt`. Document this in coverage.
