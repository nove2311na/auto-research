# Skill 00 — Research

## Identity

| Field | Value |
|---|---|
| Stage id | `00_research` |
| Owning agent | `researcher` |
| Schema | `schemas/00_research.json` |
| Output format | `json` |
| `max_options` | 1 |
| `max_retries` | 3 (per `pipeline.json:13`) |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 10 MCP, Ch. 14 RAG |
| Claude Code book chapters | Ch. 5 MCP, Ch. 8 Prompt Craft |

## Input schema

### Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `input_ref` | string (path/URL/topic) | yes | hcom message from `@orch` |
| `depth` | enum: `shallow` \| `medium` \| `deep` | yes (default `medium`) | `--depth` CLI flag |

### Depth parameters (per `agents/researcher/AGENT.md:31-33`)

| Depth | Rounds | Queries/round | Source cap |
|---|---|---|---|
| `shallow` | 1 | 3 | ≤5 |
| `medium` (default) | 2 | 5 | ≤10 |
| `deep` | 3 | 3-5 | ≤15 |

### Example hcom message

```bash
hcom send --name <sender> "@research-pipeline-claude-8 research: abc12345 depth=medium; input=inputs/inbox/qec.txt; schema=schemas/00_research.json"
```

### Source

- `schemas/00_research.json` — required: `topic`, `depth`, `queries`, `sources`, `synthesis`
- `agents/researcher/AGENT.md:21-32` — input prose description

## Process

1. **(LLM-decided)** Read the hcom message. Extract `input_id`, `input_ref`, `depth`.
2. **(deterministic)** Compute the subject.
   - If `input_ref` is a topic string in a `.txt` file → use as-is.
   - Otherwise call `tools.fetch_input.fetch(input_ref)` and extract the main subject in 1-2 sentences.
3. **(LLM-decided)** Look up depth parameters (table above).
4. **(LLM-decided)** Round 1: generate N initial queries covering different angles — definition, current state, key players, recent developments, criticism. Record each in `queries[]` with `round: 1` + a short `rationale`.
5. **(deterministic)** For each query: call `WebSearch`. Collect URLs. Dedupe by URL across the round.
6. **(LLM-decided + deterministic hybrid)** Pick the top URLs (cap per depth). For each: call `WebFetch`, extract 200-500 char excerpt, append to `sources[]` with `url`, `title`, `excerpt`, `fetched_at`, `relevance`.
7. **(LLM-decided)** If not at last round: identify gaps, generate follow-up queries, run another round. Do NOT re-fetch URLs already in `sources[]`.
8. **(LLM-decided)** Write `synthesis` (500-2000 word integrated summary with `[N]` inline citations).
9. **(LLM-decided)** Write `key_findings` (3-7 bullets — the most important points).
10. **(LLM-decided)** Write `gaps` (1-3 honest limitations).
11. **(deterministic)** Assemble the JSON matching `schemas/00_research.json`. Write via `tools.artifact_io.write_artifact` + `write_meta`.

```python
from tools.artifact_io import build_meta, write_meta, write_artifact, next_version
v = next_version(input_id, "00_research")
write_artifact(input_id, "00_research", v, dossier_json, ext="json")
meta = build_meta(
    stage="00_research", input_id=input_id, version=v,
    producer="researcher", parent_ref=str(input_ref),
)
write_meta(input_id, "00_research", v, meta)  # validation: pending
```

12. **(deterministic)** Ping `@critic` with `validate: <input_id> 00_research`.

## Output schema (artifact template)

### Top-level required fields (per `schemas/00_research.json`)

| Field | Type | Constraint |
|---|---|---|
| `topic` | string | `minLength: 1` |
| `depth` | string | enum: `shallow` \| `medium` \| `deep` |
| `queries` | array | `minItems: 1`; each item has `query`, `round` |
| `sources` | array | each item has `url` (uri), `title`, `excerpt` (`minLength: 1`) |
| `synthesis` | string | `minLength: 1`; ~500-2000 words with inline `[N]` citations |

### Optional fields

| Field | Type | Notes |
|---|---|---|
| `key_findings` | array of strings | 3-7 bullets (per `agents/researcher/AGENT.md:50-51`) |
| `gaps` | array of strings | 1-3 honest limitations (per `:52-53`) |
| `sources[].relevance` | enum | `high` \| `medium` \| `low` |
| `sources[].fetched_at` | date-time | ISO 8601 |

### Field-by-field template

```json
{
  "topic": "<one sentence, specific>",
  "depth": "medium",
  "queries": [
    {
      "query": "<the search query>",
      "round": 1,
      "rationale": "<why this angle>",
      "results_count": 8
    }
  ],
  "sources": [
    {
      "url": "https://example.com/page",
      "title": "<page title>",
      "fetched_at": "2026-06-01T12:00:00Z",
      "excerpt": "<200-500 char excerpt relevant to topic>",
      "relevance": "high"
    }
  ],
  "synthesis": "<500-2000 word integrated summary with [1], [2] citations>",
  "key_findings": [
    "<most important takeaway 1>",
    "<most important takeaway 2>"
  ],
  "gaps": [
    "<honest limitation 1>"
  ]
}
```

## Example

### Real (lifted from `scripts/smoke_v2.py:18-45`)

```json
{
  "topic": "Quantum error correction 2026",
  "depth": "medium",
  "queries": [
    {"query": "quantum error correction 2026 advances", "round": 1, "rationale": "broad scoping", "results_count": 8},
    {"query": "topological codes Google IBM 2025", "round": 1, "rationale": "key players", "results_count": 6},
    {"query": "surface code threshold recent papers", "round": 2, "rationale": "gap from round 1", "results_count": 5},
    {"query": "logical qubit overhead criticism", "round": 2, "rationale": "limitations", "results_count": 4}
  ],
  "sources": [
    {"url": "https://example.com/qec-review-2026", "title": "QEC Review 2026", "fetched_at": "2026-06-01T12:00:00Z",
     "excerpt": "Surface codes remain dominant; logical qubit counts crossed 1000 in 2026 demonstrations.",
     "relevance": "high"},
    {"url": "https://example.com/google-condor-2025", "title": "Google Condor Update", "fetched_at": "2026-06-01T12:01:00Z",
     "excerpt": "Google's 1000+ qubit Condor processor achieved below-threshold surface code operation.",
     "relevance": "high"}
  ],
  "synthesis": "Quantum error correction matured significantly in 2026. Surface codes dominate due to their high threshold (~1%) and planar geometry. Google's Condor and IBM's Heron R3 both demonstrated below-threshold operation with 1000+ logical qubits [1][2]. Key challenges remain: logical qubit overhead (1000:1 physical:logical), real-time decoding latency, and crosstalk in 2D arrays.",
  "key_findings": [
    "Surface codes crossed the 1000 logical qubit milestone in 2026",
    "Below-threshold operation now routine for distances d=5 to d=11",
    "Real-time decoding latency remains the bottleneck for fault-tolerant gates"
  ],
  "gaps": [
    "Limited public data on long-term (week-scale) logical qubit stability",
    "Color codes largely unexplored in recent industrial demonstrations"
  ]
}
```

## Self-check checklist (pre-submit, numbered)

- [ ] **Schema:** all `required` fields present (`topic`, `depth`, `queries`, `sources`, `synthesis`)
- [ ] **Depth enum:** `depth` ∈ `shallow` \| `medium` \| `deep`
- [ ] **Queries:** `queries[]` non-empty; each has `query` (minLength 1) + `round` (integer ≥1)
- [ ] **Sources:** each `source` has `url` (uri format), `title`, `excerpt` (minLength 1)
- [ ] **Citations:** every `[N]` in `synthesis` resolves to a 1-based index in `sources[]`
- [ ] **Topic:** one sentence, specific (not "AI" — "the current state of open-weights LLM safety research as of 2026")
- [ ] **Queries diverse:** round 1 is not 5 variants of the same phrase
- [ ] **Sources weighted:** `relevance: high` only for actually-cited sources in `synthesis`
- [ ] **Synthesis as one piece:** not stapled per-source paragraphs
- [ ] **Gaps honest:** "We found nothing on X" is better than pretending coverage was complete
- [ ] **Meta:** sibling `v1.meta.json` written via `build_meta` + `write_meta` (even for shallow / 1-source case)
- [ ] **Handoff:** `@critic` pinged with `validate: <input_id> 00_research`

## Validation

- **Which check:** `validation/02-post-execution-completeness.md` + `validation/03-llm-judge.md` (per `tools/validator.py`)
- **Threshold:** `pipeline.json` → `critic.llm_judge_threshold` = 0.7
- **Common failure → fix:**
  - `synthesis` empty or `minLength: 1` violated → write at least 500 words, add inline citations
  - `queries` empty (`minItems: 1` violated) → generate at least 1 query
  - `[N]` citation doesn't resolve to `sources[]` index → re-number or add the missing source
  - LLM-judge scores < 0.7 (e.g. "queries are too narrow", "synthesis reads as a list") → re-write with broader queries + connected prose

## Failure modes

- **WebSearch returns 0 results** → record the query with `results_count: 0`, try a reformulation, note in `gaps`. (`agents/researcher/AGENT.md:97-99`)
- **WebFetch times out / 4xx / 5xx** → skip that URL, retry ≤1, note in `gaps` if it was a key source. (`:100`)
- **Topic is ambiguous** (e.g. "transformers") → pick most likely subject from search-result context, record disambiguation in `gaps`. (`:101-103`)
- **All sources are low-quality** (SEO spam) → still produce the dossier; flag source-quality concern in `gaps`. (`:104-105`)

## Refactor delta

- **Scope:** Small
- **Current state:** 12-step process inlined in `agents/researcher/AGENT.md:21-63`. No numbered pre-submit checklist. No formal example.
- **Target state:** This skill spec. The 12-step process moves here. The agent's AGENT.md trims to ~60 lines.
- **Concrete steps:**
  1. Promote "Quality bar" (`:83-93`) + "Failure modes" (`:96-105`) to numbered pre-submit + failure-modes sections of this skill spec. Done (above).
  2. Add `minItems: 3` to `schemas/00_research.json#key_findings` and `maxItems: 3` to `#gaps` (per the prose rules in `:50-53`).
  3. Add a `maxLength: 5000` to `schemas/00_research.json#synthesis` (currently unbounded; should have an upper limit to prevent runaway).
  4. Move the depth-parameters table (`:31-33`) into this spec's Identity section. Done (above).
  5. Cite this spec from `agents/researcher/AGENT.md` "Step-by-step" section.

## Source files (for traceability)

- `agents/researcher/AGENT.md` — runtime prompt
- `schemas/00_research.json` — the contract
- `tools/artifact_io.py` — `build_meta`, `write_meta`, `write_artifact`
- `tools/fetch_input.py` — `fetch`, `input_id_for`
- `pipeline.json:8-15` — `00_research` stage config
- `AGENTS.md` invariant #6 — research first
- `agents/orchestrator/AGENT.md:44-49` — inbound handoff template
- `scripts/smoke_v2.py:18-45` — real example
