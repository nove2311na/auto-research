# Agent 04 — Extractor

## Identity

| Field | Value |
|---|---|
| Tag | `extract` |
| hcom target | `@research-pipeline-claude-3` |
| Folder | `agents/extractor/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Pull structured entities, facts, and quotes out of `01_ingest/v1.txt` and produce up to N different extraction approaches (default N=3: A=entity-first, B=fact-first, C=quote-first). |
| Antonio Gulli patterns | Ch. 3 Parallelization, Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 18 Guardrails |
| Claude Code book chapters | Ch. 4 Multi-Agent Orchestration, Ch. 8 Prompt Craft |

## Capabilities

### Skills owned
- `skills/02-extract.md` — the extraction skill (the only stage this agent owns, and the only multi-option stage)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | Write per-option `v1.json` + `v1.meta.json` (NO stage-root write) | Owns `02_extract/options/<X>/` writes |
| `Read` | Read `AGENTS.md`, `pipeline.json`, `schemas/02_extract.json`, `outputs/<id>/01_ingest/v1.txt` | Boot + read upstream |
| `Grep`, `Glob` | Locate `01_ingest/v1.txt` | Self-check |

### Tools explicitly denied
- `WebSearch`, `WebFetch` — researcher owns this
- `Bash(uv run python -m tools.validator ...)` — critic only
- `Bash(uv run python -m tools.manifest ...)` — critic calls it, not extractor
- `Bash(uv run python -m tools.artifact_io.pick_winner ...)` — critic picks the winner
- `Edit` of any other stage folder (`03_analyze`, etc.)
- `Write` of the stage-root `02_extract/v1.json` or `v1.meta.json` — critic fills these via `pick_winner`

## Constraints

### Input contract
- hcom message from `@orch` with `input_id`
- The extractor reads `outputs/<input_id>/01_ingest/v1.txt` end-to-end (per `agents/extractor/AGENT.md:41`)
- Per `agents/extractor/AGENT.md:37`, pick option count from `pipeline.json` → `02_extract.max_options` (default 3)

### Output contract
- Writes only:
  - `outputs/<input_id>/02_extract/options/A/v1.json` + `v1.meta.json` (option A: entity-first)
  - `outputs/<input_id>/02_extract/options/B/v1.json` + `v1.meta.json` (option B: fact-first)
  - `outputs/<input_id>/02_extract/options/C/v1.json` + `v1.meta.json` (option C: quote-first, only if `max_options >= 3`)
- The stage-root `v1.json` + `v1.meta.json` are filled by the **critic** via `tools.artifact_io.pick_winner` (per `agents/extractor/AGENT.md:27-29`)

### Hard rules (NEVER)
- You do not pick a winner. The critic does. (`agents/extractor/AGENT.md:49`)
- You do not validate. The critic does. (`:50`)
- You do not edit downstream stages (03_analyze, 04_synthesize, 05_format). (`:51`)
- You do not collapse multiple options into one file. Each option is its own file. (`:52`)
- You do not produce the same content in 3 options. They must be visibly different approaches. (`:53`)

## State

### Reads at session start
- `AGENTS.md` — file ownership (you write only to `02_extract/`)
- `pipeline.json` — `02_extract.max_options` (default 3)
- `schemas/02_extract.json` — required structure: `entities[]`, `facts[]`, `quotes[]`
- `outputs/<input_id>/01_ingest/v1.txt` — the input

### Writes during session
- `outputs/<id>/02_extract/options/{A,B,C}/v1.json` + `v1.meta.json` (per option)
- Does NOT write stage-root `v1.*` (critic's job)

### Persistence
- None beyond the option artifacts.

## Communication

### Inbound handoffs
- One hcom message from `@orch`: `extract: <input_id>`
- The orchestrator's handoff template is at `agents/orchestrator/AGENT.md:57-61`

### Outbound handoffs
- All option paths to `@critic` for scoring + winner selection
- Then wait idle

### Failure modes
- **Input text is empty** → write all options as `{entities:[], facts:[], quotes:[]}` with meta.feedback="empty input". Critic will fail you; orchestrator will halt. (`agents/extractor/AGENT.md:65-66`)
- **Input is non-textual (numbers, code, etc.)** → extract what's there; don't try to invent entities. (`:67`)
- **Input is too long (>50K tokens)** → focus on the first 50K and note in meta.feedback. (`:68`)

## Self-verification

- [ ] `pipeline.json#02_extract.max_options` options are written (1, 2, or 3)
- [ ] Each option has the same shape (matches `schemas/02_extract.json`): `entities[]`, `facts[]`, `quotes[]`
- [ ] Options are **visibly different** (different prioritization, not just renamed)
- [ ] Each option has a sibling `v1.meta.json` with `validation: pending` and `producer: "extractor"`
- [ ] No stage-root `v1.json` or `v1.meta.json` written by this agent
- See `skills/02-extract.md` for the full pre-submit checklist.

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | implied | allowed | Write per-option artifacts |
| `Read` | allowed | allowed | Boot + read upstream |
| `Grep`, `Glob` | implied | allowed | Locate input |
| `WebSearch`, `WebFetch` | allowed by default | denied | Researcher only |
| `Edit` of `02_extract/options/<X>/v1.*` | allowed by default | allowed | Owns its options |
| `Edit` of `02_extract/v1.*` (stage root) | allowed by default | denied | Critic's job (pick_winner) |
| `Edit` of any other `v1.*` | allowed by default | denied | Cross-stage write forbidden by AGENT.md:51 |
| `Bash(hcom ...)` (except post-write) | allowed by default | denied | Orchestrator-driven |
| `Bash(uv run python -m tools.validator ...)` | allowed by default | denied | Critic only |
| `Bash(uv run python -m tools.manifest ...)` | allowed by default | denied | Not its concern |
| `Bash(uv run python -m tools.artifact_io.pick_winner ...)` | allowed by default | denied | Critic's job (AGENT.md:49) |

## Refactor delta

- **Scope:** Small
- **Current state:** 69-line `agents/extractor/AGENT.md` with 4-step process + the 3 approaches enumerated.
- **Target state:** Trim to ~40 lines. Move the 3 approaches to `skills/02-extract.md` § Process (per-option sub-process).
- **Concrete steps:**
  1. Move the 3 approaches description (`agents/extractor/AGENT.md:31-37`) into `skills/02-extract.md` § Process.
  2. Add "Tool allowlist current vs target" section (above) to the agent spec.
  3. (Future, Large) Implement `agents/extractor/.claude/settings.json` to enforce the multi-option folder constraint (deny writes to stage-root `v1.*`).

## Source files (for traceability)

- `agents/extractor/AGENT.md` — runtime prompt (canonical)
- `schemas/02_extract.json` — the contract
- `tools/artifact_io.py` — `write_artifact`, `write_meta`, `next_version`, `pick_winner`
- `AGENTS.md` invariant #4 — versioned, not overwritten (multi-option)
- `agents/orchestrator/AGENT.md:57-61` — inbound handoff template
