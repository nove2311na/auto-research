---
name: 00-research
description: >
  Produces a research dossier via iterative WebSearch + WebFetch rounds; matches
  the 00_research stage. Use when the orchestrator kicks off a new research
  pipeline input and depth is shallow/medium/deep.
---

# Skill 00 — Research

## Identity
- Stage id: `00_research`
- Owning agent: `researcher`
- Schema: `schemas/00_research.json` (required: `topic`, `depth`, `queries`, `sources`, `synthesis`)
- Output format: `json`
- `max_options`: 1, `max_retries`: 3

## Input schema
| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `input_ref` | string (path/URL/topic) | yes | hcom message from `@orch` |
| `depth` | enum: `shallow`\|`medium`\|`deep` | yes (default `medium`) | `--depth` CLI flag |

### Depth parameters
| Depth | Rounds | Queries/round | Source cap |
|---|---|---|---|
| `shallow` | 1 | 3 | ≤5 |
| `medium` (default) | 2 | 5 | ≤10 |
| `deep` | 3 | 3-5 | ≤15 |

## Process (see `skill.json#process` for the structured form)

1. Read hcom message. Extract `input_id`, `input_ref`, `depth`.
2. **(deterministic)** Compute subject. Topic string → use as-is. Otherwise call `tools.fetch_input.fetch()` and extract main subject in 1-2 sentences.
3. **(LLM)** Round 1: generate N initial queries (definition, current state, key players, recent developments, criticism).
4. **(deterministic)** For each query: `WebSearch`. Collect URLs. Dedupe by URL.
5. **(LLM + deterministic)** For each top URL: `WebFetch`, extract 200-500 char excerpt, append to `sources[]`.
6. **(LLM)** If not last round: identify gaps, generate follow-ups, run another round. Do NOT re-fetch URLs.
7. **(LLM)** Write `synthesis` (500-2000 words with `[N]` inline citations).
8. **(LLM)** Write `key_findings` (3-7 bullets) + `gaps` (1-3 honest limitations).
9. **(deterministic)** Assemble JSON matching `schemas/00_research.json`. Write via `tools.artifact_io.write_artifact` + `write_meta`.
10. **(deterministic)** Ping `@critic` with `validate: <input_id> 00_research`.

## Output schema (artifact template)
See `skill.json#output_schema` for the JSON form. Required top-level:
- `topic` (string, minLength 1)
- `depth` (enum)
- `queries[]` (minItems 1; each has `query` + `round`)
- `sources[]` (each has `url` uri, `title`, `excerpt` minLength 1)
- `synthesis` (string, minLength 1; ~500-2000 words with `[N]` inline citations)

Optional: `key_findings[]`, `gaps[]`.

## Self-check (see `skill.json#self_check` for the full numbered list)
- All `[N]` citations in `synthesis` resolve to `sources[]` indices
- `topic` is one sentence, specific
- Round 1 queries are diverse
- `relevance: high` only for actually-cited sources
- `synthesis` is one piece (not stapled per-source paragraphs)
- `gaps` are honest
- `v1.meta.json` written even for shallow / 1-source case

## Validation
- Deterministic: `tools.validator.schema_check` + `completeness_check` (Draft-7)
- LLM-judge: critic scores 0-1; pass if ≥ `pipeline.json` → `critic.llm_judge_threshold` (default 0.7)
- Common failure: `[N]` citation doesn't resolve → re-number or add missing source

## Source
Full spec: `.docs/agentic/skills/00-research.md`. JSON form: `.claude/skills/00-research/skill.json`. Real example: `scripts/smoke_v2.py:18-45`.
