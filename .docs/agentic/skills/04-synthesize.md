# Skill 04 — Synthesize

## Identity

| Field | Value |
|---|---|
| Stage id | `04_synthesize` |
| Owning agent | `synthesizer` |
| Schema | `schemas/04_synthesize.json` |
| Output format | `json` |
| `max_options` | 1 |
| `max_retries` | 3 |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 16 Reasoning Techniques (narrative), Ch. 18 Guardrails (min-items) |
| Claude Code book chapters | Ch. 3 Context Engineering, Ch. 8 Prompt Craft |

## Input schema

### Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `03_analyze/v1.json` | file path | yes (read end-to-end) | upstream artifact |
| `02_extract/v1.json` | file path | yes (for cross-reference to facts) | upstream artifact |
| `00_research/v1.json` | file path | optional (for `key_findings` in thesis evidence) | upstream artifact (if 00_research ran) |

### Example hcom message

```bash
hcom send --name <sender> "@research-pipeline-claude-5 synthesize: abc12345; input=outputs/abc12345/03_analyze/v1.json; schema=schemas/04_synthesize.json"
```

### Source

- `schemas/04_synthesize.json` — required: `summary`, `insights`, `narrative`, `diagrams`, `theses`
- `agents/synthesizer/AGENT.md:9-12` — input prose

## Process

1. **(LLM-decided)** Read `03_analyze/v1.json`, `02_extract/v1.json`, optionally `00_research/v1.json`.
2. **(LLM-decided)** Form a mental model of "what is this source about, and what's the most important takeaway?"
3. **(LLM-decided)** Compose the artifact matching `schemas/04_synthesize.json`:
   - `summary`: 1-3 sentence TL;DR. Must stand alone.
   - `insights[]`: 3-7 distinct insights. Each has `insight` (1-2 sentence claim), `grounding` (which theme/gap/contradiction from `03_analyze`), `novelty` (high/medium/low).
   - `narrative`: 1-3 paragraph connected piece that weaves the insights together.
   - `diagrams[]`: **2-5** diagrams of mixed types. At minimum one `flowchart` and one `mindmap`. (Per `agents/synthesizer/AGENT.md:27-37`.)
   - `theses[]`: **2-5** synthesized positions. Each has `statement`, `evidence[]` (drawn from `02_extract.facts` or `00_research.key_findings`), `counterarguments[]` (1-3), `confidence` (high/medium/low). (Per `:38-45`.)
4. **(deterministic)** Write `v1.json` to `outputs/<id>/04_synthesize/v1.json`.
5. **(deterministic)** Write `v1.meta.json` with `validation: pending`.
6. **(deterministic)** Ping `@critic` with `validate: <input_id> 04_synthesize`.

### Diagram types (per `schemas/04_synthesize.json#diagrams[].type`)

| Type | Use case | Example |
|---|---|---|
| `flowchart` | Processes / pipelines / categories | QEC pipeline (physical → encoding → measurement → decoder → logical) |
| `mindmap` | Related concepts around a central topic | QEC landscape 2026 (Codes / Players / Challenges) |
| `sequence` | Interactions between entities over time | Handshake between decoder + control system |
| `graph` | Relationship networks | Citation graph of papers |
| `class` | Object hierarchies | Stack of error-correction code families |
| `state` | FSM | Decoder state machine |
| `concept` | Free-form concept map | Cross-cutting themes |

**Mermaid code rule:** the `code` field is **raw Mermaid syntax WITHOUT the ` ```mermaid ` wrapper** — the formatter adds that when rendering `v1.md` (per `scripts/smoke_v2.py:173`).

### Thesis rule

- `statement`: a clear claim (1 sentence)
- `evidence[]`: 2-5 supporting facts/observations, **drawn from `02_extract.facts[]` or `00_research.key_findings[]`** (not invented)
- `counterarguments[]`: 1-3 opposing views, **honestly engaged (not strawmen)**
- `confidence`: honest assessment (`high` / `medium` / `low`)

## Output schema (artifact template)

```json
{
  "summary": "<1-3 sentence TL;DR, max 1000 chars>",
  "insights": [
    {
      "insight": "<1-2 sentence claim>",
      "grounding": "<reference to theme/gap/contradiction from 03_analyze>",
      "novelty": "high|medium|low"
    }
  ],
  "narrative": "<1-3 paragraph connected piece>",
  "diagrams": [
    {
      "type": "flowchart",
      "title": "<short title>",
      "code": "<raw Mermaid syntax, NO ```mermaid wrapper>",
      "description": "<optional 1-line>"
    },
    {
      "type": "mindmap",
      "title": "<short title>",
      "code": "<raw Mermaid syntax>",
      "description": "<optional>"
    }
  ],
  "theses": [
    {
      "statement": "<clear claim>",
      "evidence": ["<fact 1>", "<fact 2>"],
      "counterarguments": ["<opposing view 1>"],
      "confidence": "high|medium|low"
    }
  ]
}
```

## Example

### Real (lifted from `scripts/smoke_v2.py:108-132`)

```json
{
  "summary": "Quantum error correction crossed industrial viability in 2026 with 1000+ logical qubits via surface codes, but overhead and decoding latency remain critical bottlenecks.",
  "insights": [
    {
      "insight": "Surface codes are the de facto standard for 2026 industrial QEC",
      "grounding": "themes: surface code dominance, industrial scaling",
      "novelty": "medium"
    }
  ],
  "narrative": "The past year marked a turning point for quantum error correction, as multiple platforms achieved below-threshold operation with hundreds to thousands of logical qubits. Yet the path to fault-tolerant quantum computing still hinges on solving the decoder-latency problem and reducing physical-to-logical overhead.",
  "diagrams": [
    {
      "type": "flowchart",
      "title": "QEC Pipeline",
      "code": "flowchart LR\n  A[Physical Qubits] --> B[Surface Code Encoding]\n  B --> C[Stabilizer Measurements]\n  C --> D[Real-time Decoder]\n  D --> E[Logical Qubit]",
      "description": "The error correction cycle from physical measurement to logical qubit output."
    },
    {
      "type": "mindmap",
      "title": "QEC Landscape 2026",
      "code": "mindmap\n  root((QEC 2026))\n    Codes\n      Surface\n      Color\n      Subsystem\n    Players\n      Google\n      IBM\n      IonQ\n    Challenges\n      Overhead\n      Decoding\n      Crosstalk"
    }
  ],
  "theses": [
    {
      "statement": "Surface codes will dominate industrial QEC for the next 3-5 years",
      "evidence": [
        "1000+ logical qubit demonstrations in 2026",
        "Mature fabrication processes favor planar codes",
        "Below-threshold operation routine"
      ],
      "counterarguments": [
        "Color codes have better transversal gate sets",
        "LDPC codes could leapfrog surface codes if overhead drops"
      ],
      "confidence": "high"
    },
    {
      "statement": "Decoder latency, not qubit count, is the real bottleneck to fault tolerance",
      "evidence": [
        "Real-time decoding required for syndrome extraction cycles",
        "Classical hardware scaling limited by interconnect bandwidth"
      ],
      "counterarguments": [
        "FPGA-based decoders already operate at MHz rates for small codes",
        "ML decoders may unlock latency gains"
      ],
      "confidence": "medium"
    }
  ]
}
```

## Self-check checklist (pre-submit, numbered)

- [ ] **Schema:** all `required` fields present (`summary`, `insights`, `narrative`, `diagrams`, `theses`)
- [ ] **Summary standalone:** `summary` is 1-3 sentences; readable without any other context; ≤1000 chars (per `schemas/04_synthesize.json#summary.maxLength: 1000`)
- [ ] **Insights count:** `insights[]` has 3-7 entries (per `agents/synthesizer/AGENT.md:19`); each has `insight` + `grounding` (required)
- [ ] **Insights grounded:** each insight references a theme/gap/contradiction from `03_analyze` (no floating insights)
- [ ] **Novelty enum:** each `insights[].novelty` ∈ `high` | `medium` | `low`
- [ ] **Narrative connected:** `narrative` is 1-3 paragraphs; reads as one piece (not 5 stapled paragraphs)
- [ ] **Diagrams count:** `diagrams[]` has ≥2 entries
- [ ] **Diagram types:** at least one `flowchart` AND one `mindmap` (per `agents/synthesizer/AGENT.md:28`)
- [ ] **Diagram code:** `code` field is Mermaid syntax WITHOUT the ```` ```mermaid ```` wrapper (formatter adds it; per `scripts/smoke_v2.py:173`)
- [ ] **Diagram type enum:** each `diagrams[].type` ∈ `flowchart` | `sequence` | `mindmap` | `graph` | `class` | `state` | `concept`
- [ ] **Theses count:** `theses[]` has ≥2 entries (per `agents/synthesizer/AGENT.md:38, 53-54`)
- [ ] **Thesis evidence:** each `theses[].evidence[]` is drawn from `02_extract.facts[]` or `00_research.key_findings[]` (no invented evidence)
- [ ] **Thesis counterarguments:** each `theses[].counterarguments[]` has 1-3 entries, honestly engaged
- [ ] **Thesis confidence enum:** each `theses[].confidence` ∈ `high` | `medium` | `low`
- [ ] **No invented facts:** every claim traces to `02_extract` or `00_research`
- [ ] **Meta complete:** `v1.meta.json` has `producer: "synthesizer"`, `validation.status: "pending"`
- [ ] **Handoff:** `@critic` pinged with `validate: <input_id> 04_synthesize`

## Validation

- **Which check:** `validation/02-post-execution-completeness.md` + `validation/03-llm-judge.md`
- **Threshold:** 0.7
- **Common failure → fix:**
  - `diagrams` has <2 entries (or no `flowchart`/`mindmap`) → add diagrams; review Mermaid syntax mentally before writing
  - `theses` has <2 entries → add another thesis with 2-3 evidence + 1-2 counterarguments
  - `summary` exceeds 1000 chars → trim to 1-3 punchy sentences
  - LLM-judge scores < 0.7 (e.g. "insights float", "narrative reads as a list", "diagrams don't render") → re-ground insights, rewrite narrative as a connected piece, fix Mermaid syntax

## Failure modes

- **Empty 03_analyze** → output a summary that says so: `summary: "Source material had no extractable themes."` Critic will fail it. (`agents/synthesizer/AGENT.md:64`)
- **Too many insights** → 3-7 is the sweet spot. More than 10 and the narrative falls apart. (`:65`)
- **Mermaid syntax errors** → 0 diagrams with valid code → critic's LLM-judge will catch; agent should test syntax mentally before writing

## Refactor delta

- **Scope:** Medium
- **Current state:** Diagrams + theses types inlined in `agents/synthesizer/AGENT.md:27-45`. The `≥2 diagrams + ≥2 theses` rule is in the prompt (`:53-54`) but NOT in `schemas/04_synthesize.json` (no `minItems`).
- **Target state:** This skill spec owns the diagrams + theses detail. The agent's AGENT.md trims. Schema gains `minItems: 2` to make the rule deterministic.
- **Concrete steps:**
  1. Move the diagrams+theses types (`agents/synthesizer/AGENT.md:27-45`) into this spec's Process section. Done (above).
  2. Add `minItems: 2` to `schemas/04_synthesize.json#diagrams` and `#theses`. (Schema change; makes the rule deterministic.)
  3. Add `minItems: 1, maxItems: 7` to `schemas/04_synthesize.json#insights` (currently no upper bound; the LLM-judge is the only enforcement for "3-7 is the sweet spot").
  4. Add `maxLength: 3000` to `schemas/04_synthesize.json#narrative` (currently unbounded).
  5. Cite this spec from `agents/synthesizer/AGENT.md` "Step-by-step" section.

## Source files (for traceability)

- `agents/synthesizer/AGENT.md` — runtime prompt
- `schemas/04_synthesize.json` — the contract (needs `minItems` for diagrams + theses)
- `tools/artifact_io.py` — `write_artifact`, `write_meta`
- `pipeline.json:43-51` — `04_synthesize` stage config
- `AGENTS.md` invariant #2 — every artifact has a sibling meta
- `agents/orchestrator/AGENT.md:68-71` — inbound handoff template
- `scripts/smoke_v2.py:108-132` — real example (1 flowchart + 1 mindmap + 2 theses)
