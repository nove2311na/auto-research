# Skill 02 — Extract

## Identity

| Field | Value |
|---|---|
| Stage id | `02_extract` |
| Owning agent | `extractor` |
| Schema | `schemas/02_extract.json` |
| Output format | `json` (one per option, in `options/A/`, `options/B/`, `options/C/`) |
| `max_options` | 3 (per `pipeline.json:32`; can be 1 or 2) |
| `max_retries` | 3 |
| Antonio Gulli patterns | Ch. 3 Parallelization, Ch. 5 Tool Use, Ch. 10 MCP |
| Claude Code book chapters | Ch. 5 MCP, Ch. 8 Prompt Craft |

> **This is the only multi-option stage.** The critic picks the winner via `tools.artifact_io.pick_winner` and copies it to the stage root.

## Input schema

### Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `01_ingest/v1.txt` | file path | yes (read end-to-end) | upstream artifact |

### Example hcom message

```bash
hcom send --name <sender> "@research-pipeline-claude-3 extract: abc12345; input=outputs/abc12345/01_ingest/v1.txt; schema=schemas/02_extract.json; produce options/A,B,C"
```

### Source

- `schemas/02_extract.json` — required: `entities[]`, `facts[]`, `quotes[]`
- `agents/extractor/AGENT.md:41` — input prose ("Read `01_ingest/v1.txt` end-to-end")

## Process

1. **(LLM-decided)** Read `01_ingest/v1.txt` end-to-end.
2. **(LLM-decided)** Determine option count from `pipeline.json` → `02_extract.max_options` (default 3; can be 1 or 2).
3. **For each option letter A, B, C...** (parallelizable):
   - **(LLM-decided)** Compose the extraction JSON matching `schemas/02_extract.json` for the chosen approach.
   - **(deterministic)** Write `options/<X>/v1.json` via `tools.artifact_io.write_artifact`.
   - **(deterministic)** Write `options/<X>/v1.meta.json` via `build_meta` + `write_meta` (validation: pending).

### The 3 approaches (per `agents/extractor/AGENT.md:31-37`)

- **Option A: entity-first** — maximize entity coverage. People/orgs/concepts first, then facts and quotes that mention them.
- **Option B: fact-first** — maximize fact coverage. Atomic claims with evidence quotes, then entities and quotes.
- **Option C: quote-first** — maximize verbatim quotes with attribution, then entities/facts that explain them.

### Field constraints (per `schemas/02_extract.json`)

| Field | Type | Constraint |
|---|---|---|
| `entities[]` | array of objects | each has `name` (minLength 1), `type` (enum), `mentions` (integer ≥0); optional `aliases` |
| `entities[].type` | enum | `person` \| `org` \| `place` \| `concept` \| `product` \| `event` \| `other` |
| `facts[]` | array of objects | each has `claim` (minLength 1), `evidence_quote` (minLength 1); optional `confidence` |
| `facts[].confidence` | enum | `high` \| `medium` \| `low` |
| `quotes[]` | array of objects | each has `text` (minLength 1), `attribution` |

### Sub-process per option

```python
# For option A (entity-first), e.g.:
artifact = {
  "entities": [
    {"name": "Google", "type": "org", "mentions": 4, "aliases": ["Alphabet"]},
    {"name": "Surface code", "type": "concept", "mentions": 5}
  ],
  "facts": [
    {"claim": "Surface codes have ~1% threshold",
     "evidence_quote": "high threshold (~1%)",
     "confidence": "high"}
  ],
  "quotes": []
}
v = next_version(input_id, "02_extract", option="A")
write_artifact(input_id, "02_extract", v, json.dumps(artifact), ext="json", option="A")
meta = build_meta(stage="02_extract", input_id=input_id, version=v,
                  producer="extractor", parent_ref="01_ingest/v1.txt")
write_meta(input_id, "02_extract", v, meta, option="A")
```

4. **(deterministic)** Send all paths to `@critic` with the request: "score each option 0-1, pick the best, copy to stage root as v1.json, then run validator on the winner".
5. **(deterministic)** Sit idle until `@orch` responds.

### Critic's pick (informs the extractor)

The critic calls `tools.artifact_io.pick_winner(input_id, "02_extract", option_scores, ext="json")` → copies the highest-scoring option's `options/<X>/v1.json` to `v1.json` at the stage root, with `picked_option` and `picked_score` in `v1.meta.json`. Then re-validates the stage-root copy.

## Output schema (artifact template)

### Per-option (`options/<X>/v1.json`)

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

### Stage root (`v1.json` — filled by critic, not extractor)

Same shape as per-option, but lives at `outputs/<id>/02_extract/v1.json`. The `v1.meta.json` has additional `picked_option` and `picked_score` fields.

## Example

### Real (lifted from `scripts/smoke_v2.py:74-86` — this is a single "winner" variant; in a real 3-option run there'd be 3 distinct files)

```json
{
  "entities": [
    {"name": "Google", "type": "org", "mentions": 4},
    {"name": "IBM", "type": "org", "mentions": 3},
    {"name": "Surface code", "type": "concept", "mentions": 5},
    {"name": "Condor processor", "type": "product", "mentions": 2}
  ],
  "facts": [
    {"claim": "Surface codes have ~1% threshold", "evidence_quote": "high threshold (~1%)", "confidence": "high"},
    {"claim": "1000+ logical qubits demonstrated in 2026", "evidence_quote": "logical qubit counts crossed 1000", "confidence": "high"}
  ],
  "quotes": []
}
```

### Synthetic 3-option variant (V2 — `smoke_v2.py` does not exercise this yet)

- **Option A** (entity-first): `entities[]` is the largest array; `facts[]` and `quotes[]` are minimal.
- **Option B** (fact-first): `facts[]` is the largest array; each fact has a long `evidence_quote`; `entities[]` is minimal.
- **Option C** (quote-first): `quotes[]` is non-empty (verbatim from the source); `entities[]` and `facts[]` are minimal.

## Self-check checklist (pre-submit, numbered)

- [ ] **Option count:** exactly `pipeline.json#02_extract.max_options` files written (1, 2, or 3)
- [ ] **Schema:** each option matches `schemas/02_extract.json` (entities/facts/quotes arrays present)
- [ ] **Entities quality:** each entity has `name` (minLength 1), `type` (enum), `mentions` (integer ≥0); no "various people" vague entities (per `agents/extractor/AGENT.md:58`)
- [ ] **Facts quality:** each fact has `claim` (atomic 1-sentence) + `evidence_quote` (short quote from source); no unsourced claims (per `:59`)
- [ ] **Quotes quality:** each quote is verbatim with attribution; no paraphrasing (per `:60`)
- [ ] **Options visibly different:** the 3 options are not the same content; they prioritize different fields (per `:53-54`)
- [ ] **No stage-root write:** agent did NOT write `outputs/<id>/02_extract/v1.json` or `v1.meta.json` (critic's job via `pick_winner`)
- [ ] **Meta per option:** each option has a sibling `v1.meta.json` with `validation: pending` and `producer: "extractor"`
- [ ] **Handoff:** all option paths sent to `@critic`

## Validation

- **Which check:** `validation/02-post-execution-completeness.md` (per option) + `validation/03-llm-judge.md` (per option + winner selection)
- **Threshold:** 0.7
- **Common failure → fix:**
  - `entities[].type` not in enum → re-classify (e.g. "AI" → `concept`, not custom)
  - `facts[].evidence_quote` empty or paraphrased → copy a verbatim span from the source
  - 3 options look the same → regenerate; option A should be entity-dominant, B fact-dominant, C quote-dominant
  - Winner selection contested (LLM-judge tied) → critic's tiebreak: highest schema+completeness score wins; document in feedback

## Failure modes

- **Input text is empty** → write all options as `{entities:[], facts:[], quotes:[]}` with meta.feedback="empty input". Critic will fail you; orchestrator will halt. (`agents/extractor/AGENT.md:65-66`)
- **Input is non-textual (numbers, code, etc.)** → extract what's there; don't try to invent entities. (`:67`)
- **Input is too long (>50K tokens)** → focus on the first 50K and note in meta.feedback. (`:68`)

## Refactor delta

- **Scope:** Medium
- **Current state:** 4-step process inlined in `agents/extractor/AGENT.md:41-46`; the 3 approaches (A/B/C) described at `:31-37`. `scripts/smoke_v2.py` only exercises a single "winner" variant, not the 3-option case.
- **Target state:** This skill spec owns the 3-approach detail. The agent's AGENT.md trims. A 3-option smoke variant exercises `pick_winner` end-to-end.
- **Concrete steps:**
  1. Move the 3-approaches description (`:31-37`) into this spec's Process section. Done (above).
  2. Add a 3-option variant to `scripts/smoke_v2.py` (build `options/A/v1.json`, `B/v1.json`, `C/v1.json` with deliberately different shapes; assert `pick_winner` picks correctly).
  3. Add `minItems: 1` to `schemas/02_extract.json#entities` (currently 0 — the critic's LLM-judge is the only enforcement for "at least 1 entity"). For the smoke test in `smoke_v2.py:74-86`, the artifact has 4 entities, so this is safe.
  4. Add `minItems: 1` to `schemas/02_extract.json#facts` similarly.
  5. Cite this spec from `agents/extractor/AGENT.md` "Step-by-step" section.

## Source files (for traceability)

- `agents/extractor/AGENT.md` — runtime prompt
- `schemas/02_extract.json` — the contract
- `tools/artifact_io.py` — `write_artifact`, `write_meta`, `next_version`, `pick_winner`
- `pipeline.json:25-33` — `02_extract` stage config (max_options: 3)
- `AGENTS.md` invariant #4 — versioned, not overwritten (multi-option)
- `agents/orchestrator/AGENT.md:57-61` — inbound handoff template
- `scripts/smoke_v2.py:74-86` — real example (single-option variant)
