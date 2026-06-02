---
name: 02-extract
description: >
  Pulls structured entities, facts, quotes from 01_ingest/v1.txt; produces up to
  3 different extraction approaches (A=entity-first, B=fact-first,
  C=quote-first). The only multi-option stage. Use when the orchestrator hands
  off to the extractor; critic will pick the winner.
---

# Skill 02 — Extract

## Identity
- Stage id: `02_extract`
- Owning agent: `extractor`
- Schema: `schemas/02_extract.json` (required: `entities[]`, `facts[]`, `quotes[]`)
- Output format: `json` (one per option, in `options/A/`, `options/B/`, `options/C/`)
- `max_options`: 3 (per `pipeline.json:32`; can be 1 or 2)
- `max_retries`: 3

## Input schema
| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `01_ingest/v1.txt` | file path | yes (read end-to-end) | upstream artifact |

## Process (see `skill.json#process` for the structured form)

1. **(LLM)** Read `01_ingest/v1.txt` end-to-end.
2. **(LLM)** Determine option count from `pipeline.json` → `02_extract.max_options` (default 3).
3. **For each option letter A, B, C (parallelizable):**
   - **(LLM)** Compose the extraction JSON for the chosen approach.
   - **(deterministic)** Write `options/<X>/v1.json` + `options/<X>/v1.meta.json`.

### The 3 approaches
- **Option A: entity-first** — maximize entity coverage (people/orgs/concepts first, then facts and quotes that mention them).
- **Option B: fact-first** — maximize fact coverage (atomic claims with evidence quotes, then entities and quotes).
- **Option C: quote-first** — maximize verbatim quotes with attribution, then entities/facts that explain them.

4. **(deterministic)** Send all option paths to `@critic` with the request: "score each option 0-1, pick the best, copy to stage root as v1.json, then run validator on the winner".
5. **(deterministic)** Sit idle until `@orch` responds.

## Output schema (artifact template)
See `skill.json#output_schema` for the JSON form.

Per-option shape (`options/<X>/v1.json`):
```json
{
  "entities": [
    {"name": "<name>", "type": "<person|org|place|concept|product|event|other>", "mentions": 0, "aliases": []}
  ],
  "facts": [
    {"claim": "<atomic claim, 1 sentence>", "evidence_quote": "<short quote from source>", "confidence": "<high|medium|low>"}
  ],
  "quotes": [
    {"text": "<verbatim quote>", "attribution": "<who said it>"}
  ]
}
```

Stage root (`v1.json`) is filled by the critic via `pick_winner` — same shape, with `picked_option` and `picked_score` in `v1.meta.json`.

## Self-check (see `skill.json#self_check` for the full numbered list)
- Exactly `pipeline.json#02_extract.max_options` files written
- Each option matches `schemas/02_extract.json` (entities/facts/quotes arrays present)
- 3 options are visibly different (different prioritization, not just renamed)
- Each option has a sibling `v1.meta.json` with `validation: pending` and `producer: "extractor"`
- Agent did NOT write stage-root `v1.json` (critic's job via `pick_winner`)

## Validation
- Per-option schema+completeness + LLM-judge
- Critic's `pick_winner` selects highest-scoring option (tiebreak: schema+completeness)
- Common failure: 3 options look the same → regenerate; option A entity-dominant, B fact-dominant, C quote-dominant

## Source
Full spec: `.docs/agentic/skills/02-extract.md`. JSON form: `.claude/skills/02-extract/skill.json`. Real example: `scripts/smoke_v2.py:74-86` (single-winner variant).
