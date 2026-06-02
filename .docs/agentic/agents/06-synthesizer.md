# Agent 06 — Synthesizer

## Identity

| Field | Value |
|---|---|
| Tag | `synth` |
| hcom target | `@research-pipeline-claude-5` |
| Folder | `agents/synthesizer/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Turn the analysis into a coherent narrative with insights, TL;DR, Mermaid diagrams, and theses. Single option. |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 16 Reasoning Techniques (narrative + theses), Ch. 18 Guardrails (≥2 diagrams + ≥2 theses) |
| Claude Code book chapters | Ch. 3 Context Engineering, Ch. 4 Multi-Agent Orchestration, Ch. 8 Prompt Craft |

## Capabilities

### Skills owned
- `skills/04-synthesize.md` — the synthesis skill (the only stage this agent owns)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | Write `v1.json` + `v1.meta.json` | Owns `04_synthesize/` writes |
| `Read` | Read `AGENTS.md`, `schemas/04_synthesize.json`, `03_analyze/v1.json`, `02_extract/v1.json` (for facts), `00_research/v1.json` (for key_findings) | Boot + read upstreams |

### Tools explicitly denied
- `WebSearch`, `WebFetch` — researcher owns this
- `Edit` of any other stage folder
- `Bash(uv run python -m tools.validator ...)` — critic only
- `Bash(uv run python -m tools.manifest ...)` — not its concern
- `Bash(hcom ...)` except post-write ping

## Constraints

### Input contract
- hcom message from `@orch` with `input_id`
- Reads:
  - `outputs/<input_id>/03_analyze/v1.json` (required)
  - `outputs/<input_id>/02_extract/v1.json` (for cross-reference to facts)
  - `outputs/<input_id>/00_research/v1.json` (optional; for `key_findings` in thesis evidence)

### Output contract
- Writes only:
  - `outputs/<input_id>/04_synthesize/v1.json` (matches `schemas/04_synthesize.json`)
  - `outputs/<input_id>/04_synthesize/v1.meta.json` (producer meta)

### Hard rules (NEVER)
- You do not introduce facts that weren't in 02_extract. Synthesize, don't fabricate. (`agents/synthesizer/AGENT.md:50`)
- You do not produce a list of bullet points where a narrative is required. (`:51`)
- You do not validate. Critic decides. (`:52`)
- **You must produce at least 2 diagrams and 2 theses.** Empty `diagrams: []` or `theses: []` will fail the critic's completeness check. (`:53-54`)

## State

### Reads at session start
- `AGENTS.md` — file ownership (you write only to `04_synthesize/`)
- `schemas/04_synthesize.json` — required structure
- `outputs/<input_id>/03_analyze/v1.json`
- `outputs/<input_id>/02_extract/v1.json` (for cross-reference to facts)
- `tools/artifact_io.py`

### Writes during session
- `outputs/<id>/04_synthesize/v1.json` + `v1.meta.json`

### Persistence
- None beyond the artifact.

## Communication

### Inbound handoffs
- One hcom message from `@orch`: `synthesize: <input_id>`
- The orchestrator's handoff template is at `agents/orchestrator/AGENT.md:68-71`

### Outbound handoffs
- One hcom message to `@critic`: `validate: <input_id> 04_synthesize`

### Failure modes
- **Empty 03_analyze** → output a summary that says so: `summary: "Source material had no extractable themes."` Critic will fail it. (`agents/synthesizer/AGENT.md:64`)
- **Too many insights** → 3-7 is the sweet spot. More than 10 and the narrative falls apart. (`:65`)
- **Mermaid syntax errors** → 0 diagrams with valid code → critic's LLM-judge will catch; agent should test syntax mentally before writing

## Self-verification

- [ ] `summary` is 1-3 sentences and stands alone (readable without any other context) per `agents/synthesizer/AGENT.md:18, 58`
- [ ] `insights[]` has 3-7 entries; each has `insight` (1-2 sentence claim), `grounding` (which theme/gap/contradiction), `novelty` (high/medium/low) per `:19-22, 59`
- [ ] `narrative` is 1-3 paragraphs that read as one piece (not 5 stapled paragraphs) per `:22, 60`
- [ ] `diagrams[]` has ≥2 entries; at least one `flowchart` and one `mindmap`; each `code` is Mermaid syntax WITHOUT the ```` ```mermaid ```` wrapper per `:27-37, 53`
- [ ] `theses[]` has ≥2 entries; each has `statement`, `evidence[]` (drawn from `02_extract.facts` or `00_research.key_findings`), `counterarguments[]`, `confidence` (high/medium/low) per `:38-45, 53-54`
- [ ] `v1.meta.json` has `producer: "synthesizer"` and `validation.status: "pending"`
- See `skills/04-synthesize.md` for the full pre-submit checklist + Mermaid examples.

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | implied | allowed | Write artifacts + meta |
| `Read` | allowed | allowed | Boot + read upstreams |
| `WebSearch`, `WebFetch` | allowed by default | denied | Researcher only |
| `Edit` of `04_synthesize/v1.*` | allowed by default | allowed | Owns its stage |
| `Edit` of any other `v1.*` | allowed by default | denied | Cross-stage write forbidden by AGENT.md |
| `Bash(hcom ...)` (except post-write) | allowed by default | denied | Orchestrator-driven |
| `Bash(uv run python -m tools.validator ...)` | allowed by default | denied | Critic only |
| `Bash(uv run python -m tools.manifest ...)` | allowed by default | denied | Not its concern |

## Refactor delta

- **Scope:** Small/Medium
- **Current state:** 65-line `agents/synthesizer/AGENT.md` with diagrams + theses detailed inline. The `≥2 diagrams + ≥2 theses` rule is in the prompt (L53-54) but NOT in `schemas/04_synthesize.json` (no `minItems`).
- **Target state:** Trim to ~30 lines. Move the diagram+thesis types to `skills/04-synthesize.md` § Process + § Output schema. Add `minItems: 2` to the schema to make the rule deterministic.
- **Concrete steps:**
  1. Move the diagrams types (`:27-37`) into `skills/04-synthesize.md` § Output schema (with Mermaid examples).
  2. Move the theses structure (`:38-45`) into `skills/04-synthesize.md` § Output schema.
  3. Add `minItems: 2` to `schemas/04_synthesize.json#diagrams` and `#theses`. (Schema change.)
  4. Add "Tool allowlist current vs target" section (above) to the agent spec.
  5. (Future, Large) Implement `agents/synthesizer/.claude/settings.json` to enforce the minItems rule at the agent level (defense in depth).

## Source files (for traceability)

- `agents/synthesizer/AGENT.md` — runtime prompt (canonical)
- `schemas/04_synthesize.json` — the contract (needs `minItems` for diagrams + theses)
- `tools/artifact_io.py` — `write_artifact`, `write_meta`
- `AGENTS.md` invariant #2 — every artifact has a sibling meta
- `agents/orchestrator/AGENT.md:68-71` — inbound handoff template
- `scripts/smoke_v2.py:115-121` — Mermaid examples to lift
