# Validation 03 — LLM-as-Judge

## Identity

| Field | Value |
|---|---|
| Surface | `llm-judge` |
| Type | LLM-decided (the critic is itself a Claude session; no SDK needed) |
| Triggered by | The critic, after schema + completeness pass |
| Antonio Gulli patterns | Ch. 4 Reflection, Ch. 18 Guardrails, **Ch. 19 Evaluation & Monitoring** |
| Claude Code book chapters | Ch. 10 Failure Modes, Ch. 12 Team Adoption |

## Purpose

- **What this checks:** Semantic quality of the artifact — not just "is it well-formed" but "is it good?" The LLM-judge is the only check that catches "schema-valid, completeness-valid, but the content is weak."
- **Why it exists:** Deterministic checks cannot assess "are the 2 diagrams actually informative?" or "does the narrative cohere?" or "are the theses grounded in the upstream facts?" — only an LLM can.

## How it works

### Algorithm

1. Critic reads the artifact at `outputs/<id>/<stage>/v<N>.<ext>`.
2. Critic runs the deterministic checks first (via `validate_artifact(input_id, stage, version, ext, llm_judge_score=None)`) — see `validation/02-post-execution-completeness.md`.
3. Critic forms a judgment on 0.0–1.0 scale, grounded in:
   - For `00_research`: queries diverse, sources weighted primary, synthesis as one piece, gaps honest (per `agents/researcher/AGENT.md:83-93`).
   - For `01_ingest`: text non-empty, dossier merged if present (per `agents/ingestor/AGENT.md`).
   - For `02_extract`: entities have name+type+mentions, facts have claim+evidence+confidence, options visibly differ (per `agents/extractor/AGENT.md:57-62`).
   - For `03_analyze`: themes supported by facts, gaps specific, contradictions real (per `agents/analyzer/AGENT.md:33-36`).
   - For `04_synthesize`: summary stands alone, insights grounded, narrative connected, ≥2 diagrams + ≥2 theses (per `agents/synthesizer/AGENT.md:57-60` and `:53-54`).
   - For `05_format`: JSON ↔ Markdown agree, no invented content, references trace to upstream (per `agents/formatter/AGENT.md:92-98`).
4. Critic re-calls `validate_artifact(..., llm_judge_score=<score>)` to record the score.

### Source of truth

- `tools/validator.py:128-137` — the recording logic (score compared against threshold, recorded in meta).
- `tools/validator.py:101-168` — `validate_artifact` (caller).
- `agents/critic/AGENT.md:21-40` — the prompt for the critic (the LLM-judge IS the critic).
- `pipeline.json` → `critic.llm_judge_threshold` (default 0.7).

### Inputs

- The artifact + its upstream context (for grounding)
- The critic's own Claude session (no API key needed; the critic is a Claude Code CLI session)

### Outputs

- A score in `0.0..1.0`
- A re-call to `validate_artifact` to record it in `v<N>.meta.json#validation`

## Pass / fail criteria

- **Pass:** score ≥ `pipeline.json` → `critic.llm_judge_threshold` (default 0.7).
- **Fail:** score < threshold.
- **Threshold:** `pipeline.json` → `critic.llm_judge_threshold` (line 65 of `pipeline.json`).
- **Retry semantics:** Fail → orchestrator retries the stage agent with the critic's feedback.

## How to invoke

### CLI (recording only — the LLM judgment is done by a Claude session)

```bash
python -m tools.validator <input_id> <stage> <version> [ext] [option]
# The score is passed via a code-level call, not a CLI flag. The CLI prints the result.
```

### From an agent prompt

The critic itself:

```python
# From agents/critic/AGENT.md L29-40
r1 = validate_artifact(input_id, stage, version, ext, llm_judge_score=None)  # deterministic
score = <my judgment, 0.0-1.0>
r2 = validate_artifact(input_id, stage, version, ext, llm_judge_score=score)  # record
hcom send --name <sender> "@research-pipeline-claude-1 verdict: <input_id> <stage>; pass|fail score={score} feedback=..."
```

### From a smoke test

- `scripts/smoke_v2.py:215` — simulates a critic with `score = 0.85` (above threshold).
- `scripts/smoke_validator.py:35-37` — same.
- `scripts/smoke_validator.py:42-44` — tests `score = 0.5` (below threshold) → fail.

## Coverage

| Stage | Applies? | Notes |
|---|---|---|
| `00_research` | yes | Quality: topic specific, queries diverse, sources primary, synthesis one piece |
| `01_ingest` | partial (TXT) | LLM-judge still applies; checks dossier-merge quality |
| `02_extract` | yes | Per-option + critic picks winner |
| `03_analyze` | yes | Themes grounded, gaps specific, contradictions real |
| `04_synthesize` | yes | Summary standalone, insights grounded, ≥2 diagrams, ≥2 theses |
| `05_format` | yes | JSON ↔ Markdown agree, no invented content |

## Failure modes

- **Score exactly at threshold** → `>=` comparison passes (`tools/validator.py:132`). Document if borderline.
- **Tie between 2+ scores** → tiebreak on schema + completeness (per `agents/critic/AGENT.md:62-66`); document the tiebreak in feedback.
- **LLM-judge contradicts deterministic checks** → the deterministic check wins. The LLM-judge is the final filter, not a co-equal one.
- **Retries exhausted (3 fails)** → orchestrator halts (per `agents/orchestrator/AGENT.md:37-38`).
- **Default to pass when in doubt** → per `agents/critic/AGENT.md:47` ("Default to pass when in doubt"). This is a known tradeoff (some false-pass at the cost of more retries).

## Refactor delta

- **Scope:** Large
- **Current state:** LLM-judge is the critic's own judgment. No shared rubric. Variance across runs is unknown.
- **Target state:** An eval rubric (JSON or prompt) that the critic references for each stage. Score dimensions: schema adherence, completeness, factual grounding, narrative coherence, Mermaid quality, etc. This makes the LLM-judge reproducible.
- **Concrete steps:**
  1. Author `tools/eval_rubric.json` with per-stage dimensions + weight.
  2. Update `agents/critic/AGENT.md` to load the rubric at session start and use it as the score prompt.
  3. Add a `scripts/smoke_llm_judge.py` that runs the same input 5 times and asserts score variance < 0.1.
  4. Track per-rubric-dimension scores in `v<N>.meta.json#validation#checks#llm_judge#dimensions` (schema change).

## Source files (for traceability)

- `tools/validator.py:128-137` — recording logic
- `tools/validator.py:101-168` — `validate_artifact`
- `pipeline.json:62-66` — `critic` block (threshold, checks)
- `agents/critic/AGENT.md:21-66` — the critic's process + the 3-checks table
- `scripts/smoke_v2.py:215` — E2E with score 0.85
- `scripts/smoke_validator.py:35-44` — focused pass/fail tests
