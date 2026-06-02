# Agent 05 — Analyzer

## Identity

| Field | Value |
|---|---|
| Tag | `analyze` |
| hcom target | `@research-pipeline-claude-4` |
| Folder | `agents/analyzer/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Find themes, gaps, and contradictions in the extracted material. Single option. Output: one `v1.json` matching `schemas/03_analyze.json`. |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 12 Exception Handling (gaps + contradictions) |
| Claude Code book chapters | Ch. 4 Multi-Agent Orchestration |

## Capabilities

### Skills owned
- `skills/03-analyze.md` — the analysis skill (the only stage this agent owns)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | Write `v1.json` + `v1.meta.json` | Owns `03_analyze/` writes |
| `Read` | Read `AGENTS.md`, `schemas/03_analyze.json`, `outputs/<id>/02_extract/v1.json` (the critic's winner) | Boot + read upstream |
| `Grep`, `Glob` | Locate `02_extract/v1.json` | Self-check |

### Tools explicitly denied
- `WebSearch`, `WebFetch` — researcher owns this
- `Edit` of any other stage folder
- `Bash(uv run python -m tools.validator ...)` — critic only
- `Bash(uv run python -m tools.manifest ...)` — not its concern
- `Bash(hcom ...)` except post-write ping

## Constraints

### Input contract
- hcom message from `@orch` with `input_id`
- Reads `outputs/<input_id>/02_extract/v1.json` end-to-end (the critic's winner, per `agents/analyzer/AGENT.md:11`)

### Output contract
- Writes only:
  - `outputs/<input_id>/03_analyze/v1.json` (themes + gaps + contradictions)
  - `outputs/<input_id>/03_analyze/v1.meta.json` (producer meta)

### Hard rules (NEVER)
- You do not pick themes from outside the source material. If a theme isn't supported by at least one fact, drop it. (`agents/analyzer/AGENT.md:27`)
- You do not invent gaps. "What's missing" should be obvious from re-reading the source. (`:28`)
- You do not validate. Critic decides. (`:29`)
- You do not write to other stages. (`:30`)

## State

### Reads at session start
- `AGENTS.md` — file ownership (you write only to `03_analyze/`)
- `schemas/03_analyze.json` — required structure
- `outputs/<input_id>/02_extract/v1.json` — the critic's winner
- `tools/artifact_io.py` — write helpers

### Writes during session
- `outputs/<id>/03_analyze/v1.json` + `v1.meta.json`

### Persistence
- None beyond the artifact.

## Communication

### Inbound handoffs
- One hcom message from `@orch`: `analyze: <input_id>`
- The orchestrator's handoff template is at `agents/orchestrator/AGENT.md:63-66`

### Outbound handoffs
- One hcom message to `@critic`: `validate: <input_id> 03_analyze`

### Failure modes
- **Empty 02_extract** → output `{themes: [], gaps: [<whole-topic-is-empty>], contradictions: []}`. Critic will fail it for being empty; orchestrator will halt. (`agents/analyzer/AGENT.md:40`)
- **Source is too short for themes** → 1 theme is OK; don't pad to 6. (`:41`)

## Self-verification

- [ ] `themes[]` has 2-6 entries; each theme's `supporting_facts` references at least one fact from `02_extract.facts[]` (per `agents/analyzer/AGENT.md:18-19, 33-34`)
- [ ] `gaps[]` has 1-5 entries; each gap's `description` is specific (not "more detail would be nice") per `:19, 35`
- [ ] `contradictions[]` has 0-3 entries; each `claim_a` and `claim_b` actually contradict (not just different angles) per `:20, 36`
- [ ] No invented themes (must be supported by facts); no invented gaps
- [ ] `v1.meta.json` has `producer: "analyzer"` and `validation.status: "pending"`
- See `skills/03-analyze.md` for the full pre-submit checklist.

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | implied | allowed | Write artifacts + meta |
| `Read` | allowed | allowed | Boot + read upstream |
| `Grep`, `Glob` | implied | allowed | Locate input |
| `WebSearch`, `WebFetch` | allowed by default | denied | Researcher only |
| `Edit` of `03_analyze/v1.*` | allowed by default | allowed | Owns its stage |
| `Edit` of any other `v1.*` | allowed by default | denied | Cross-stage write forbidden by AGENT.md:30 |
| `Bash(hcom ...)` (except post-write) | allowed by default | denied | Orchestrator-driven |
| `Bash(uv run python -m tools.validator ...)` | allowed by default | denied | Critic only |
| `Bash(uv run python -m tools.manifest ...)` | allowed by default | denied | Not its concern |

## Refactor delta

- **Scope:** Small
- **Current state:** 42-line `agents/analyzer/AGENT.md` with 5-step process inlined.
- **Target state:** Trim to ~25 lines. Move steps 2-4 (`agents/analyzer/AGENT.md:16-23`) to `skills/03-analyze.md` § Process.
- **Concrete steps:**
  1. Move the "Identify" sub-steps (themes/gaps/contradictions) into `skills/03-analyze.md` § Process.
  2. Add "Tool allowlist current vs target" section (above) to the agent spec.
  3. (Future, Large) Implement `agents/analyzer/.claude/settings.json` to enforce stage folder restriction.

## Source files (for traceability)

- `agents/analyzer/AGENT.md` — runtime prompt (canonical)
- `schemas/03_analyze.json` — the contract
- `tools/artifact_io.py` — `write_artifact`, `write_meta`, `next_version`
- `AGENTS.md` invariant #2 — every artifact has a sibling meta
- `agents/orchestrator/AGENT.md:63-66` — inbound handoff template
