# Agent 01 — Orchestrator

## Identity

| Field | Value |
|---|---|
| Tag | `orch` |
| hcom target | `@research-pipeline-claude-1` |
| Folder | `agents/orchestrator/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Pipeline conductor — routes work to stage agents, dispatches to critic, handles retries up to `max_retries`, halts on exhaustion, finalizes the manifest. |
| Antonio Gulli patterns | Ch. 2 Routing, Ch. 6 Planning, Ch. 7 Multi-Agent, Ch. 8 Memory, Ch. 11 Goal-Setting, Ch. 15 A2A, Ch. 16 Reasoning Techniques |
| Claude Code book chapters | Ch. 2 Permission Architecture, Ch. 4 Multi-Agent Orchestration, Ch. 10 Failure Modes |

## Capabilities

### Skills owned
- (none — orchestrator does not own a stage; it routes work between stages)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(hcom ...)` | Send tasks to stage agents, list active, get events | Per `.claude/settings.json` `permissions.allow` (hcom-only allowlist) |
| `Bash(uv run python -m tools.manifest ...)` | `init_manifest`, `record_attempt`, `is_done` | Orchestrator owns manifest reads |
| `Bash(uv run python -m tools.fetch_input ...)` | `input_id_for`, `fetch` (to compute input_id from `input_ref`) | To derive `input_id` before kicking off |
| `Read` | `AGENTS.md`, `pipeline.json`, `prd.json`, `learnings.md`, `progress.md` | State-on-disk pattern (Ralph Wiggum loop) |
| `Write` | `prd.json` (state), `progress.md` (audit log) | Explicit in `agents/orchestrator/AGENT.md:88-89` |
| `Grep`, `Glob` | Locate files in `outputs/`, `inputs/` | To check file presence before/after handoffs |
| `hcom bundle prepare --for self` | Bootstrap read of recent activity | Per `agents/orchestrator/AGENT.md:14` |

### Tools explicitly denied
- `WebSearch`, `WebFetch` — research is the researcher's job
- `Edit` of any `v1.*` artifact — only stage agents write artifacts
- `Edit` of `manifest.json` content — only `tools.manifest.record_attempt` and `finalize` (called by critic and formatter)
- `Edit` of `pipeline.json` — humans own this (per `AGENTS.md` invariant #1)
- `Write` to any `outputs/<id>/<stage>/v1.*` — explicitly forbidden by `agents/orchestrator/AGENT.md:86`

## Constraints

### Input contract
- hcom message with: `input_id`, `input_ref` (path/URL/topic), `depth` (default `medium`)
- Optional: list of files (for batch inputs)
- For more details, see `agents/orchestrator/AGENT.md:17-40` ("Your responsibility: drive one input through the 6 stages")

### Output contract
- Writes only:
  - `prd.json` (state file; per shape at `agents/orchestrator/AGENT.md:92-101`)
  - `progress.md` (append-only audit log; format at `agents/orchestrator/AGENT.md:103-112`)
- Does NOT write:
  - Any `v1.*` artifact
  - `manifest.json` content (only `record_attempt` + `finalize` may)

### Hard rules (NEVER)
- You do not write to any `v1.*` artifact. Only the stage agent for that stage writes content. (`agents/orchestrator/AGENT.md:86`)
- You do not call `tools.validator.validate_artifact()`. Only the critic does. (`:87`)
- You do not write `manifest.json` content. Only `record_attempt` and `finalize` from `tools.manifest`. (`:88`)
- You do write `prd.json` (state) and `progress.md` (audit log). (`:89`)
- On max-retries-exhausted, you STOP. You do not skip the stage or fake a pass. (`:90`)

## State

### Reads at session start
- `AGENTS.md` (or `CLAUDE.md` via symlink) — team invariants
- `pipeline.json` — the source of truth: stages, agents, max retries
- `prd.json` — current pipeline state (input_id, current_stage, retries)
- `learnings.md` — accumulated knowledge from prior runs
- `progress.md` — append-only audit log
- `hcom bundle prepare --for self` — what other agents have been doing

### Writes during session
- `prd.json` (read+write; the orchestrator's state file)
- `progress.md` (append-only; one line per transition)
- Does NOT write any artifact or manifest content

### Persistence
- State on disk, not in memory (per `AGENTS.md` "Ralph Wiggum loop" pattern). Each handoff reads `prd.json` to recover state.

## Communication

### Inbound handoffs
- Kickoff from `scripts/run_pipeline.sh` or `scripts/kickoff.sh` (initial orchestrator prompt)
- For each stage, after the stage agent writes its artifact: implicit (read `outputs/<id>/<stage>/v1.*`)
- After the critic validates: a `verdict: <input_id> <stage>` message back from `@critic`

### Outbound handoffs
- 6 stage handoffs (one per stage in `pipeline.json` order). Templates at `agents/orchestrator/AGENT.md:44-82`.
- 1 critic handoff per stage (`validate: <input_id> <stage> [version]`)
- (After all stages pass) implicit finalize via the formatter, who calls `tools.manifest.finalize`

### Failure modes
- **Critic returns no decision in 5 min** → re-send the validation task once. If still no response, escalate to human. (`agents/orchestrator/AGENT.md:116`)
- **Stage agent produces v1 but writes no meta** → nudge the stage agent; never write meta on its behalf. (`:117`)
- **File not at expected path** → ask the stage agent to confirm before proceeding; do not infer. (`:118`)
- **All retries exhausted** → append a `halted` entry to `progress.md`, notify (Slack if configured), halt the pipeline for this input.

## Self-verification

- [ ] `prd.json` has `current_input_id` set before the first stage handoff
- [ ] After each stage, `prd.json.current_stage` advances
- [ ] After each critic verdict, `prd.json.retries[<stage>]` increments on fail
- [ ] On all-stages-pass: `manifest.completed_at` is set (via formatter)
- [ ] On halt: `progress.md` has a `halted | <input_id>` entry
- [ ] `inputs/processed/` contains the source file (moved from `inbox/`)

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `Bash(hcom ...)` | allowed | allowed | Core coordination |
| `Bash(uv run python -m tools.manifest ...)` | implied | allowed | Manifest state read |
| `Bash(uv run python -m tools.fetch_input ...)` | implied | allowed | input_id derivation |
| `Read` | allowed | allowed | State read |
| `Write` (to `prd.json`, `progress.md` only) | allowed | allowed | Explicit by AGENT.md |
| `Grep`, `Glob` | implied | allowed | File presence check |
| `WebSearch`, `WebFetch` | (not in settings) | denied | Research is the researcher's job |
| `Edit` | allowed by default | denied | Orchestrator does not edit existing files; it writes `prd.json` from scratch |
| `Write` to `v1.*` artifacts | allowed by default | denied | Enforce via path-based restriction |

## Refactor delta

- **Scope:** Small/Medium
- **Current state:** 129-line `agents/orchestrator/AGENT.md` with all 6 handoff templates inlined.
- **Target state:** Trim to ~80 lines: keep the handoff-overview (one-line per stage) + hard rules + state shape. Replace inlined handoff templates with references to `skills/NN-*.md` handoff sections.
- **Concrete steps:**
  1. Move the 6 handoff templates (`agents/orchestrator/AGENT.md:44-82`) into the corresponding `skills/NN-*.md` files as "Communication → Outbound handoffs".
  2. Replace them in the orchestrator's AGENT.md with a 1-line table: `Stage handoff: see skills/NN-*.md § Communication`.
  3. Add an explicit "Tool allowlist current vs target" section (above) and document the proposed tightening.
  4. (Future, Large) Implement `agents/orchestrator/.claude/settings.json` with `permissions.allow` for hcom + state files only.

## Source files (for traceability)

- `agents/orchestrator/AGENT.md` — runtime prompt (canonical)
- `AGENTS.md` invariant #1, #5, #6 — pipeline source of truth, manifest is audit trail, research first
- `pipeline.json` — stage list, max_retries, max_options
- `tools/manifest.py` — `init_manifest`, `record_attempt`, `is_done`, `finalize`
- `tools/fetch_input.py` — `fetch`, `input_id_for`
- `tools/hcom_io.py` — hcom wrapper
- `scripts/run_pipeline.sh` — kickoff
- `.claude/settings.json` — global hcom-only allowlist
