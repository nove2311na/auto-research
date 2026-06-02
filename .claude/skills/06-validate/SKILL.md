---
name: 06-validate
description: >
  The critic's core skill: runs schema + completeness + LLM-judge on a stage
  artifact, writes validation.status to meta, picks winners for multi-option
  stages. Use when the orchestrator pings the critic with
  'validate: <input_id> <stage>'.
---

# Skill 06 — Validate

## Identity
- Stage id: N/A (cross-cutting; runs after every stage)
- Owning agent: `critic`
- Schema: N/A (reads `schemas/<stage>.json` for the stage being validated)
- Output format: N/A (writes `v<N>.meta.json#validation`; for `02_extract` also writes stage-root `v1.json` via `pick_winner`)
- `max_retries`: inherits from stage being validated

## Input schema
| Field | Type | Required | Source |
|---|---|---|---|
| hcom message title | string | yes | pattern: `validate: <input_id> <stage> [version]` |
| Artifact to validate | file path | yes | `outputs/<input_id>/<stage>/v<N>.<ext>` (or `options/<X>/v1.json` for multi-option) |
| LLM-judge score | float (0.0-1.0) | yes (provided by the critic itself) | the critic's own judgment |

## Process (see `skill.json#process` for the structured form)

### A. Single-option stages (`00_research`, `01_ingest`, `03_analyze`, `04_synthesize`, `05_format`)
1. **(deterministic)** Read the artifact.
2. **(deterministic)** Run `validate_artifact(..., llm_judge_score=None)` (schema + completeness).
3. **(deterministic)** If schema+completeness = fail, do NOT bother with LLM-judge.
4. **(LLM - Peer Review & Claim Audit)** Act as a conference-grade peer reviewer. Evaluate logical consistency and methodological soundness. For `04_synthesize` and `05_format`, perform a structured **Claim Audit** for each major thesis/claim:
   Draft your review comments in the `feedback` field, structured as:
   ```md
   ## Claim Audit
   - **Tuyên bố gốc:** <claim_statement>
   - **Verdict:** [giữ nguyên | giảm mức độ khẳng định | sửa đổi | loại bỏ]
   - **Bằng chứng hỗ trợ:** <trích xuất từ 02_extract hoặc 00_research>
   - **Bằng chứng thiếu hụt:** <nếu có>
   - **Nguy cơ khẳng định quá đà (Overclaim Risk):** <cao | trung bình | thấp - giải thích tại sao>
   - **Đề xuất viết lại:** <cụm từ học thuật khách quan hơn>
   ```
   Form a 0.0-1.0 quality score based on this peer review (pass threshold = 0.7). If severe overclaiming or missing evidence is found, you MUST fail the stage (score < 0.7).
5. **(deterministic)** Re-call `validate_artifact(..., llm_judge_score=score)` to record.
6. **(deterministic)** Call `tools.manifest.record_attempt(...)`.
7. **(deterministic)** Reply to `@orch` with `verdict: <input_id> <stage>` + `pass|fail score=N feedback=...`.

### B. Multi-option stages (`02_extract`)
1. **(deterministic + LLM)** For each option A/B/C: read, run schema + completeness + own LLM-judge, record in `option_scores`.
2. **(deterministic)** Pick the highest-scoring option. Call `tools.artifact_io.pick_winner(...)`.
3. **(deterministic)** Re-validate the stage-root copy with the winner's LLM-judge score.
4. **(deterministic)** Call `record_attempt(... options=3, picked=<letter>, ...)`.
5. **(deterministic)** Reply to `@orch` with the verdict.

### C. The 3 checks
| Check | Source | Pass criterion |
|---|---|---|
| `schema` | `tools.validator.schema_check` (L46-65) | Artifact matches `schemas/<stage>.json` (jsonschema Draft-7) |
| `completeness` | `tools.validator.completeness_check` (L68-98) | All `required` fields present, not null/empty-string/empty-object. Empty arrays OK. |
| `llm_judge` | YOU (this Claude session) | Score 0.0-1.0; pass if ≥ `pipeline.json` → `critic.llm_judge_threshold` (default 0.7) |

**Aggregate:** `fail` if any check fails, `pass` otherwise.

## Output schema (artifact template)
See `skill.json#output_schema` for the JSON form.

The critic does **not** write a new artifact. It writes/updates:
1. `v<N>.meta.json#validation` block (per `tools/validator.py:156-166`)
2. For `02_extract` only: stage-root `v1.json` + `v1.meta.json` (via `pick_winner`)
3. Manifest entry (per `tools/manifest.record_attempt`)
4. hcom reply to `@orch`

## Self-check (see `skill.json#self_check` for the full numbered list)
- Single-option flow: called `validate_artifact` twice (None then score)
- Multi-option flow: scored each option separately; called `pick_winner`
- Stage-root copy: for `02_extract`, `v1.json` + `v1.meta.json` exist with `picked_option` + `picked_score`
- Meta validation block: filled (status, validator, validated_at, score, feedback, checks)
- Manifest recorded: `record_attempt` called with status, score, options, picked (for multi-option)
- Did not edit `v1.json` content (only meta + stage-root copy via `pick_winner`)
- Did not overrule multi-option winner
- Defaulted to pass when in doubt (per this SKILL.md § Hard rules)

## Validation
- N/A (this IS the validation)
- Common failure: schema missing → BLOCK; orchestrator halts
- Common failure: JSON parse error → surface verbatim
- Common failure: LLM-judge tied → tiebreak on schema+completeness; document in feedback

## Source
Full spec: `.docs/agentic/skills/06-validate.md`. JSON form: `.claude/skills/06-validate/skill.json`. Agent: `.claude/agents/critic.md` / `.claude/agents/critic.json`. Runtime: `tools/validator.py`, `tools/artifact_io.pick_winner`, `tools/manifest.record_attempt`.
