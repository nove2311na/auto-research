# Skill 03 — Analyze

## Identity

| Field | Value |
|---|---|
| Stage id | `03_analyze` |
| Owning agent | `analyzer` |
| Schema | `schemas/03_analyze.json` |
| Output format | `json` |
| `max_options` | 1 |
| `max_retries` | 3 |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 12 Exception Handling (gaps + contradictions) |
| Claude Code book chapters | Ch. 8 Prompt Craft |

## Input schema

### Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `02_extract/v1.json` | file path | yes (read end-to-end; the critic's winner) | upstream artifact |

### Example hcom message

```bash
hcom send --name <sender> "@research-pipeline-claude-4 analyze: abc12345; input=outputs/abc12345/02_extract/v1.json; schema=schemas/03_analyze.json"
```

### Source

- `schemas/03_analyze.json` — required: `themes[]`, `gaps[]`, `contradictions[]`
- `agents/analyzer/AGENT.md:11` — input prose

## Process

1. **(LLM-decided)** Read `02_extract/v1.json` end-to-end.
2. **(LLM-decided)** Identify:
   - **Themes**: 2-6 clusters of facts that hang together. Each theme has `name`, `description`, `supporting_facts[]` (references to fact `claim` text from `02_extract`).
   - **Gaps**: 1-5 things the source does NOT cover but probably should. Each gap has `description` + `what_would_fill_it`.
   - **Contradictions**: 0-3 places where two facts disagree. Each has `claim_a`, `claim_b`, `explanation`.
3. **(deterministic)** Write `v1.json` to `outputs/<id>/03_analyze/v1.json`.
4. **(deterministic)** Write `v1.meta.json` with `validation: pending`.
5. **(deterministic)** Ping `@critic` with `validate: <input_id> 03_analyze`.

### Field constraints (per `schemas/03_analyze.json`)

| Field | Type | Constraint |
|---|---|---|
| `themes[]` | array of objects | each has `name` (minLength 1), `supporting_facts[]`; optional `description` |
| `gaps[]` | array of objects | each has `description` (minLength 1), `what_would_fill_it` (minLength 1) |
| `contradictions[]` | array of objects | each has `claim_a` (minLength 1), `claim_b` (minLength 1); optional `explanation` |

### Template (per theme)

```json
{
  "name": "<short theme name>",
  "description": "<one-line description>",
  "supporting_facts": [
    "<verbatim claim text from 02_extract.facts[]>",
    "..."
  ]
}
```

## Output schema (artifact template)

```json
{
  "themes": [
    {
      "name": "<short name>",
      "description": "<one line>",
      "supporting_facts": ["<claim text 1>", "<claim text 2>"]
    }
  ],
  "gaps": [
    {
      "description": "<specific gap>",
      "what_would_fill_it": "<concrete research/data needed>"
    }
  ],
  "contradictions": [
    {
      "claim_a": "<claim A verbatim from 02_extract>",
      "claim_b": "<claim B verbatim from 02_extract>",
      "explanation": "<why these contradict>"
    }
  ]
}
```

## Example

### Real (lifted from `scripts/smoke_v2.py:89-105`)

```json
{
  "themes": [
    {
      "name": "surface code dominance",
      "description": "Surface codes are the de facto industrial QEC",
      "supporting_facts": ["Surface codes have ~1% threshold"]
    },
    {
      "name": "threshold achievement",
      "description": "Multiple platforms crossed below-threshold operation",
      "supporting_facts": ["1000+ logical qubits demonstrated in 2026"]
    }
  ],
  "gaps": [
    {
      "description": "Long-term stability of logical qubits",
      "what_would_fill_it": "Multi-week coherence measurements on hardware"
    }
  ],
  "contradictions": [
    {
      "claim_a": "Academic literature claims overhead reduction",
      "claim_b": "Industrial practice still uses 1000:1 physical-to-logical ratio",
      "explanation": "Decoding overhead and syndrome measurement costs may offset theoretical savings"
    }
  ]
}
```

## Self-check checklist (pre-submit, numbered)

- [ ] **Schema:** all `required` fields present (`themes`, `gaps`, `contradictions`)
- [ ] **Themes count:** `themes[]` has 2-6 entries (per `agents/analyzer/AGENT.md:18`)
- [ ] **Themes grounded:** each theme's `supporting_facts[]` references at least one fact from `02_extract.facts[]` (use the fact's `claim` text verbatim) (per `:33-34`)
- [ ] **No invented themes:** if a theme isn't supported by at least one fact, drop it (per `:27`)
- [ ] **Gaps count:** `gaps[]` has 1-5 entries (per `:19`)
- [ ] **Gaps specific:** each gap's `description` is specific (not "more detail would be nice"; "No mention of X even though Y relies on it" is good) (per `:35`)
- [ ] **No invented gaps:** "What's missing" should be obvious from re-reading the source (per `:28`)
- [ ] **Contradictions count:** `contradictions[]` has 0-3 entries (per `:20`)
- [ ] **Contradictions real:** each `claim_a`/`claim_b` actually contradict; "two facts about the same thing from different angles" is NOT a contradiction (per `:36`)
- [ ] **Min lengths:** every `description`, `what_would_fill_it`, `name`, `claim_a`, `claim_b` is non-empty (per `schemas/03_analyze.json` `minLength: 1`)
- [ ] **Meta complete:** `v1.meta.json` has `producer: "analyzer"`, `validation.status: "pending"`
- [ ] **Handoff:** `@critic` pinged with `validate: <input_id> 03_analyze`

## Validation

- **Which check:** `validation/02-post-execution-completeness.md` + `validation/03-llm-judge.md`
- **Threshold:** 0.7
- **Common failure → fix:**
  - Theme's `supporting_facts` is empty (no fact reference) → re-ground: copy the relevant `claim` text from `02_extract.facts[]`
  - Gap is too vague → make it specific; replace "more detail would be nice" with "No mention of X even though Y relies on it"
  - Contradiction is not actually a contradiction (just different angles) → remove it
  - LLM-judge scores < 0.7 (e.g. "themes are not really supported") → re-do with stronger fact references

## Failure modes

- **Empty 02_extract** → output `{themes: [], gaps: [<whole-topic-is-empty>], contradictions: []}`. Critic will fail it for being empty; orchestrator will halt. (`agents/analyzer/AGENT.md:40`)
- **Source is too short for themes** → 1 theme is OK; don't pad to 6. (`:41`)

## Refactor delta

- **Scope:** Small
- **Current state:** 5-step process inlined in `agents/analyzer/AGENT.md:16-24`. No numbered pre-submit checklist.
- **Target state:** This skill spec owns the themes/gaps/contradictions identification details. The agent's AGENT.md trims to ~25 lines.
- **Concrete steps:**
  1. Move the "Identify" sub-steps (`:16-23`) into this spec's Process section. Done (above).
  2. Add `minItems: 2` and `maxItems: 6` to `schemas/03_analyze.json#themes` (currently 0 — the prose rules in `:18` are not schema-enforced).
  3. Add `minItems: 1` and `maxItems: 5` to `schemas/03_analyze.json#gaps`.
  4. Add `maxItems: 3` to `schemas/03_analyze.json#contradictions`.
  5. Cite this spec from `agents/analyzer/AGENT.md` "Step-by-step" section.

## Source files (for traceability)

- `agents/analyzer/AGENT.md` — runtime prompt
- `schemas/03_analyze.json` — the contract
- `tools/artifact_io.py` — `write_artifact`, `write_meta`
- `pipeline.json:34-42` — `03_analyze` stage config
- `AGENTS.md` invariant #2 — every artifact has a sibling meta
- `agents/orchestrator/AGENT.md:63-66` — inbound handoff template
- `scripts/smoke_v2.py:89-105` — real example
