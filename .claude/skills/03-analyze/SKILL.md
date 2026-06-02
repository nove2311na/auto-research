---
name: 03-analyze
description: >
  Finds themes, gaps, contradictions in 02_extract/v1.json (the critic's
  winner); emits 03_analyze/v1.json. Use when the orchestrator hands off to
  the analyzer; the synthesizer will use this for narrative + theses.
---

# Skill 03 — Analyze

## Identity
- Stage id: `03_analyze`
- Owning agent: `analyzer`
- Schema: `schemas/03_analyze.json` (required: `themes[]`, `gaps[]`, `contradictions[]`)
- Output format: `json`
- `max_options`: 1, `max_retries`: 3

## Input schema
| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `02_extract/v1.json` | file path | yes (read end-to-end; the critic's winner) | upstream artifact |

## Process (see `skill.json#process` for the structured form)

1. **(LLM)** Read `02_extract/v1.json` end-to-end.
2. **(LLM)** Identify:
   - **Themes**: 2-6 clusters of facts. Each has `name`, `description`, `supporting_facts[]` (references to fact `claim` text from `02_extract`).
   - **Gaps**: 1-5 things the source does NOT cover but should. Each has `description` + `what_would_fill_it`.
   - **Contradictions**: 0-3 places where two facts disagree. Each has `claim_a`, `claim_b`, `explanation`.
3. **(deterministic)** Write `v1.json` to `outputs/<id>/03_analyze/v1.json`.
4. **(deterministic)** Write `v1.meta.json` (validation: pending).
5. **(deterministic)** Ping `@critic` with `validate: <input_id> 03_analyze`.

## Output schema (artifact template)
See `skill.json#output_schema` for the JSON form.

```json
{
  "themes": [
    {"name": "<short name>", "description": "<one line>", "supporting_facts": ["<claim text 1>"]}
  ],
  "gaps": [
    {"description": "<specific gap>", "what_would_fill_it": "<concrete research/data needed>"}
  ],
  "contradictions": [
    {"claim_a": "<verbatim from 02_extract>", "claim_b": "<verbatim from 02_extract>", "explanation": "<why these contradict>"}
  ]
}
```

## Self-check (see `skill.json#self_check` for the full numbered list)
- `themes[]` has 2-6 entries
- Each theme's `supporting_facts[]` references ≥1 fact from `02_extract.facts[]` (verbatim `claim` text)
- No invented themes (must be supported by facts); no invented gaps
- `gaps[]` has 1-5 entries; each `description` is specific
- `contradictions[]` has 0-3 entries; each `claim_a`/`claim_b` actually contradict
- Min lengths: every `description`, `what_would_fill_it`, `name`, `claim_a`, `claim_b` non-empty

## Validation
- Schema + completeness + LLM-judge
- Common failure: theme's `supporting_facts` empty → re-ground with `claim` text from `02_extract.facts[]`
- Common failure: contradiction not actually a contradiction (just different angles) → remove

## Source
Full spec: `.docs/agentic/skills/03-analyze.md`. JSON form: `.claude/skills/03-analyze/skill.json`. Real example: `scripts/smoke_v2.py:89-105`.
