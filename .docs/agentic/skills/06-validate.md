# Skill 06 — Validate

## Identity

| Field | Value |
|---|---|
| Stage id | N/A (cross-cutting; runs after every stage) |
| Owning agent | `critic` (Agent 07) |
| Schema | N/A (reads `schemas/<stage>.json` for the stage being validated) |
| Output format | N/A (writes `v<N>.meta.json#validation` block; for `02_extract` also writes stage-root `v1.json` via `pick_winner`) |
| `max_options` | N/A |
| `max_retries` | inherits from stage being validated |
| Antonio Gulli patterns | Ch. 4 Reflection, Ch. 18 Guardrails, **Ch. 19 Evaluation & Monitoring** |
| Claude Code book chapters | Ch. 10 Failure Modes, Ch. 12 Team Adoption |

> **This is the critic's core competency.** It is not a pipeline stage; it is the validation gate that runs after every stage.

## Input schema

### Fields

| Field | Type | Required | Source |
|---|---|---|---|
| hcom message title | string | yes | pattern: `validate: <input_id> <stage> [version]` |
| Artifact to validate | file path | yes | `outputs/<input_id>/<stage>/v<N>.<ext>` (or `options/<X>/v1.json` for multi-option) |
| LLM-judge score | float (0.0-1.0) | yes (provided by the critic itself) | the critic's own judgment |

### Example hcom message

```bash
hcom send --name <sender> "@research-pipeline-claude-6 validate: abc12345 02_extract; path=outputs/abc12345/02_extract/options/{A,B,C}/v1.json; schema=schemas/02_extract.json"
```

### Source

- `agents/critic/AGENT.md:17-40` — the validation process
- `tools/validator.py` — `validate_artifact`, `schema_check`, `completeness_check`
- `tools/artifact_io.py` — `pick_winner`, `write_meta`, `read_meta`
- `tools/manifest.py` — `record_attempt`
- `pipeline.json:62-66` — `critic` block (checks + threshold)

## Process

### A. Single-option stages (`00_research`, `01_ingest`, `03_analyze`, `04_synthesize`, `05_format`)

1. **(deterministic)** Read the artifact at `outputs/<id>/<stage>/v<N>.<ext>`.
2. **(deterministic)** Run `validate_artifact(input_id, stage, version, ext, llm_judge_score=None)`:
   - Schema check: `jsonschema.Draft7Validator` against `schemas/<stage>.json` (TXT stages get `status: skip`).
   - Completeness check: all `required` fields present, non-null, non-`""`, non-`{}`.
3. **(deterministic)** If schema + completeness = `fail`, do NOT bother with LLM-judge — surface the error.
4. **(LLM-decided)** Read the artifact. Form a 0.0-1.0 quality score grounded in the per-stage "quality bar" (see `agents/<role>/AGENT.md` "Quality bar" sections + `skills/<stage>.md` "Self-check checklist" sections).
5. **(deterministic)** Re-call `validate_artifact(input_id, stage, version, ext, llm_judge_score=score)` to record the score.
6. **(deterministic)** Call `tools.manifest.record_attempt(input_id, stage, version, status, score, feedback=...)`.
7. **(deterministic)** Reply to `@orch` with `verdict: <input_id> <stage>` + `pass|fail score=N feedback=...`.

### B. Multi-option stages (`02_extract`)

1. **(deterministic + LLM-decided hybrid)** For each option A, B, C:
   - Read the option's `v1.json`.
   - Run schema + completeness + your LLM-judge score.
   - Record the score in a `{option: score}` dict.
2. **(deterministic)** Pick the highest-scoring option (the winner). Call `tools.artifact_io.pick_winner(input_id, "02_extract", option_scores, ext="json")`:
   - Copies the winner's `v1.json` to the stage root.
   - Writes `v1.meta.json` with `picked_option` + `picked_score`.
3. **(deterministic)** Re-validate the stage-root copy with the winner's LLM-judge score.
4. **(deterministic)** Call `record_attempt(input_id, "02_extract", 1, status, score, options=3, picked=<letter>, feedback=...)`.
5. **(deterministic)** Reply to `@orch` with the verdict.

### C. The 3 checks table (per `agents/critic/AGENT.md:52-59`)

| Check | Source | Pass criterion |
|---|---|---|
| `schema` | `tools.validator.schema_check` (L46-65) | Artifact matches `schemas/<stage>.json` (jsonschema Draft-7) |
| `completeness` | `tools.validator.completeness_check` (L68-98) | All `required` fields present AND not null/empty-string/empty-object. Empty arrays ARE allowed. |
| `llm_judge` | YOU (this Claude session) | Score 0.0-1.0; pass if ≥ `pipeline.json` → `critic.llm_judge_threshold` (default 0.7) |

**Aggregate:** status is `fail` if any check fails, `pass` otherwise. The LLM-judge check is what only the critic can do; the first two are deterministic.

## Output schema (artifact template)

### What the critic writes

The critic does **not** write a new artifact. It writes/updates:

1. **`v<N>.meta.json#validation`** block (per `tools/validator.py:156-166`):
   ```json
   {
     "validation": {
       "status": "pass|fail",
       "validator": "critic",
       "validated_at": "2026-06-01T12:00:00Z",
       "score": 0.85,
       "feedback": "all checks passed",
       "checks": {
         "schema": "pass|fail|skip",
         "completeness": "pass|fail|skip",
         "llm_judge": "pass|fail|skip"
       }
     }
   }
   ```

2. **For `02_extract` only:** stage-root `v1.json` + `v1.meta.json` (via `pick_winner`):
   ```json
   {
     "picked_option": "B",
     "picked_score": 0.88,
     "validation": { ... }
   }
   ```

3. **Manifest entry** (per `tools/manifest.record_attempt`):
   ```json
   {
     "version": 1,
     "status": "pass|fail",
     "score": 0.85,
     "options": 3,           // only for multi-option
     "picked": "B",          // only for multi-option
     "feedback": "..."
   }
   ```

4. **hcom reply to `@orch`:**
   ```
   verdict: <input_id> <stage>
   pass|fail score=0.85 feedback=...
   ```

## Example

### Real: scoring a single option

From `scripts/smoke_validator.py:34-44`:

```python
# After running pre-check with llm_judge_score=None
r1 = validate_artifact(INPUT_ID, STAGE, 1, ext="json", llm_judge_score=None)
# r1 = {"status": "pass", "score": 0.8 (default), "feedback": "all checks passed", "checks": {...}}

# Critic's LLM-judge: 0.85
score = 0.85
r2 = validate_artifact(INPUT_ID, STAGE, 1, ext="json", llm_judge_score=score)
# r2 = {"status": "pass", "score": 0.85, "feedback": "all checks passed", ...}
assert r2["status"] == "pass" and r2["score"] == 0.85
```

### Real: below-threshold (fail)

From `scripts/smoke_validator.py:42-44`:

```python
fail = validate_artifact(INPUT_ID, STAGE, 2, ext="json", llm_judge_score=0.5)
# fail = {"status": "fail", "score": 0.0, "feedback": "failed checks: ['llm_judge']. first error: score 0.50 < threshold 0.70", ...}
assert fail["status"] == "fail"
```

### Synthetic: multi-option winner pick

```python
# Critic scores 3 options
option_scores = {"A": 0.78, "B": 0.92, "C": 0.81}
# Winner: B (highest score)
winner, version = pick_winner(input_id, "02_extract", option_scores, ext="json")
# winner = "B", version = 1
# Side effect: copies options/B/v1.json → 02_extract/v1.json
#            writes v1.meta.json with picked_option=B, picked_score=0.92

# Re-validate the stage-root copy with the winner's score
result = validate_artifact(input_id, "02_extract", 1, ext="json", llm_judge_score=0.92)
record_attempt(input_id, "02_extract", 1, result["status"],
               score=result["score"], options=3, picked="B",
               feedback=result["feedback"])
```

## Self-check checklist (pre-submit, numbered)

For the **critic** agent only:

- [ ] **Single-option flow:** called `validate_artifact` twice (once for schema+completeness with `llm_judge_score=None`, once to record LLM-judge)
- [ ] **Multi-option flow:** scored each option separately; called `pick_winner` with the correct `option_scores` dict
- [ ] **Stage-root copy:** for `02_extract`, the stage-root `v1.json` + `v1.meta.json` exist with `picked_option` + `picked_score`
- [ ] **Meta validation block:** `v<N>.meta.json#validation` is filled: `status`, `validator` (="critic"), `validated_at`, `score`, `feedback`, `checks` (with schema/completeness/llm_judge)
- [ ] **Manifest recorded:** `record_attempt` called with correct `status`, `score`, and (for multi-option) `options` + `picked`
- [ ] **Reply to `@orch`:** includes `pass|fail`, `score=`, `feedback=` (for retries)
- [ ] **Did not edit `v1.json` content:** only meta + stage-root copy via `pick_winner`
- [ ] **Did not overrule multi-option winner:** winner is the highest-scoring option, no editorial override
- [ ] **Did not self-validate:** the critic never validates its own work (N/A here, but principle holds)
- [ ] **Threshold respected:** pass iff score ≥ `pipeline.json` → `critic.llm_judge_threshold` (default 0.7)
- [ ] **Defaulted to pass when in doubt** (per `agents/critic/AGENT.md:47`)
- [ ] **Tiebreak documented** (per `:65`): if scores tied, picked the one with higher schema+completeness; documented in feedback

## Validation

- **Which check:** N/A (this IS the validation). The critic is the only validator (per `AGENTS.md` invariant #3).
- **Threshold:** `pipeline.json` → `critic.llm_judge_threshold` (default 0.7)
- **Common failure → fix:**
  - Schema missing → BLOCK; orchestrator halts; fix by ensuring `schemas/<stage>.json` exists
  - JSON parse error → surface verbatim; orchestrator halts; fix by re-writing the artifact
  - LLM-judge tied → tiebreak on schema+completeness; document in feedback
  - All 3 retries fail → feedback says "exhausted retries; orchestrator should halt"

## Failure modes

- **Schema file missing for this stage** → BLOCK with feedback "schema missing: <path>". Orchestrator halts. (`agents/critic/AGENT.md:63`)
- **Artifact is not valid JSON** → schema check fails with the parse error. Surface it in feedback. (`:64`)
- **LLM judge returns a tie** → pick the option that ranks higher on schema + completeness. Document the tiebreak in feedback. (`:65`)
- **All 3 retries fail** → write feedback that explicitly says "exhausted retries; orchestrator should halt". Record each attempt in manifest. (`:66`)

## Refactor delta

- **Scope:** Large
- **Current state:** 67-line `agents/critic/AGENT.md` with the 3-checks table inlined. The LLM-judge is the critic's own judgment — no shared rubric, so scores may vary across runs.
- **Target state:** This skill spec owns the 3-checks table + multi-option process. An eval rubric (JSON or prompt) makes the LLM-judge reproducible.
- **Concrete steps:**
  1. Move the 3-checks table (`agents/critic/AGENT.md:52-59`) into this spec's Process section "C. The 3 checks table". Done (above).
  2. Move the multi-option process (`:35-39`) into this spec's Process section "B. Multi-option stages". Done (above).
  3. Author `tools/eval_rubric.json` with per-stage dimensions + weight (per `refactor-plan.md`).
  4. Update `agents/critic/AGENT.md` to load the rubric at session start and use it as the LLM-judge prompt.
  5. Add per-rubric-dimension scores to `v<N>.meta.json#validation#checks#llm_judge#dimensions` (schema change).
  6. Add `scripts/smoke_llm_judge.py` that runs the same input 5 times and asserts score variance < 0.1.
  7. Cite this spec from `agents/critic/AGENT.md` "What you do per handoff" section.

## Source files (for traceability)

- `agents/critic/AGENT.md` — runtime prompt
- `tools/validator.py` — `validate_artifact`, `schema_check`, `completeness_check`
- `tools/artifact_io.py` — `pick_winner`, `write_meta`, `read_meta`
- `tools/manifest.py` — `record_attempt`
- `pipeline.json:62-66` — `critic` block (threshold default 0.7)
- `AGENTS.md` invariant #3 — "Critic is the only validator"
- `agents/orchestrator/AGENT.md:73-76` — inbound handoff template
- `scripts/smoke_v2.py:208-222` — E2E exercise (calls `validate_artifact` per stage)
- `scripts/smoke_validator.py` — focused pass/fail/empty-array tests
