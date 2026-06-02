# Agent 03 — Ingestor

## Identity

| Field | Value |
|---|---|
| Tag | `ingest` |
| hcom target | `@research-pipeline-claude-2` |
| Folder | `agents/ingestor/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Normalize any source (text/URL/PDF/DOCX) → plain text at `01_ingest/v1.txt`, merging the research dossier from `00_research/v1.json` if present. |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 10 MCP (file-type dispatch), Ch. 18 Guardrails |
| Claude Code book chapters | Ch. 4 Multi-Agent Orchestration |

## Capabilities

### Skills owned
- `skills/01-ingest.md` — the ingest skill (the only stage this agent owns)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(uv run python -m tools.fetch_input ...)` | `fetch(<input_ref>)` → `(text, meta)` | Core dispatch by file type / URL |
| `Bash(uv run python -m tools.artifact_io ...)` | Write `v1.txt` + `v1.json` (optional) + `v1.meta.json` | Owns `01_ingest/` writes |
| `Read` | Read `AGENTS.md`, `pipeline.json`, `schemas/01_ingest.json`, `tools/*` | Boot |
| `Grep`, `Glob` | Locate `00_research/v1.json` to merge | Deterministic merge step |

### Tools explicitly denied
- `WebSearch`, `WebFetch` — researcher owns this
- `Edit` of any other stage folder
- `Bash(hcom ...)` except post-write ack
- `Bash(uv run python -m tools.validator ...)` — critic only
- `Bash(uv run python -m tools.manifest ...)` — orchestrator only
- `Bash(uv run python -m tools.fetch_input.move_to_processed ...)` — orchestrator moves files (per `agents/ingestor/AGENT.md:83`)

## Constraints

### Input contract
- hcom message from `@orch` with `input_ref` (path/URL/topic)
- For multi-input batch, each input gets its own input_id; agent processes **one per hcom message** (per `agents/ingestor/AGENT.md:84`)

### Output contract
- Writes only:
  - `outputs/<input_id>/01_ingest/v1.txt` (primary, plain text)
  - `outputs/<input_id>/01_ingest/v1.json` (optional, matches `schemas/01_ingest.json` with `text` + `metadata`)
  - `outputs/<input_id>/01_ingest/v1.meta.json` (producer meta)
- Sibling meta carries `metadata.research_ref = "00_research/v1.json"` if dossier was merged (per `agents/ingestor/AGENT.md:73`)

### Hard rules (NEVER)
- You do not edit other stages. Your writes go only to `01_ingest/`. (`agents/ingestor/AGENT.md:80`)
- You do not validate your own work. The critic decides pass/fail. (`:81`)
- You do not call `validator.validate_artifact`. Only the critic does. (`:82`)
- You do not move files from `inputs/inbox/` to `inputs/processed/`. The orchestrator does that. (`:83`)
- For multi-input batch, each input gets its own input_id and run. You process ONE per hcom message. (`:84`)
- **If `00_research/v1.json` exists, you MUST merge it into the ingest text.** The synthesizer relies on having research context. (`:85-86`)

## State

### Reads at session start
- `AGENTS.md` — file ownership
- `pipeline.json` — confirm `01_ingest` config (max_retries, max_options=1)
- `schemas/01_ingest.json` — the contract
- `tools/fetch_input.py` — source dispatch
- `tools/artifact_io.py` — atomic write helpers

### Writes during session
- `outputs/<id>/01_ingest/v1.txt` (required)
- `outputs/<id>/01_ingest/v1.json` (optional)
- `outputs/<id>/01_ingest/v1.meta.json` (required)

### Persistence
- None beyond the artifact. The merge step reads `00_research/v1.json` but does not cache it.

## Communication

### Inbound handoffs
- One hcom message from `@orch`: `ingest: <input_id>` with `<input_ref>` in the description
- The orchestrator's handoff template is at `agents/orchestrator/AGENT.md:51-55`

### Outbound handoffs
- One ack hcom message back to `@orch` with the path
- Then one hcom message to `@critic`: `validate: <input_id> 01_ingest`

### Failure modes
- **URL fetch fails (404, timeout, 5xx)** → write meta with `validation.pending` and a note in the feedback field; orchestrator routes to critic for failure handling. (`agents/ingestor/AGENT.md:110`)
- **PDF is encrypted or scanned (no text layer)** → write what you can extract; meta.feedback says "no text layer; downstream may be empty". (`:111`)
- **Source > 1 MB** → truncate at 1 MB with a note. Don't try to be clever. (`:112`)
- **Source is a batch directory** → process the first file only; tell @orch there are N more waiting. (`:113`)
- **Defensive: `00_research/v1.json` missing** → proceed without merging; leave `metadata.research_ref` absent. (`:38-39`)

## Self-verification

- [ ] `v1.txt` is non-empty UTF-8
- [ ] If `00_research/v1.json` existed, `v1.txt` ends with `## Research Context` block containing dossier `synthesis` + numbered `[N]` sources + `key_findings` bullets
- [ ] If dossier was merged, `v1.meta.json` has `metadata.research_ref = "00_research/v1.json"`
- [ ] `v1.meta.json` has `producer: "ingestor"` and `validation.status: "pending"`
- [ ] `parent_ref` in meta is the original `input_ref`
- See `skills/01-ingest.md` for the full pre-submit checklist.

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `Bash(uv run python -m tools.fetch_input ...)` | implied | allowed | Source dispatch |
| `Bash(uv run python -m tools.artifact_io ...)` | implied | allowed | Write artifacts + meta |
| `Read` | allowed | allowed | Boot |
| `Grep`, `Glob` | implied | allowed | Find `00_research/v1.json` |
| `WebSearch`, `WebFetch` | allowed by default | denied | Researcher owns this |
| `Edit` of `01_ingest/v1.*` | allowed by default | allowed | Owns its stage |
| `Edit` of any other `v1.*` | allowed by default | denied | Cross-stage write forbidden by AGENT.md:80 |
| `Bash(hcom ...)` (except post-write) | allowed by default | denied | Orchestrator-driven |
| `Bash(uv run python -m tools.validator ...)` | allowed by default | denied | Critic only |
| `Bash(uv run python -m tools.manifest ...)` | allowed by default | denied | Not its concern |
| `Bash(... move_to_processed ...)` | allowed by default | denied | Orchestrator's job (AGENT.md:83) |

## Refactor delta

- **Scope:** Small
- **Current state:** 114-line `agents/ingestor/AGENT.md` with 5-step process + merge logic inlined at lines 42-75.
- **Target state:** Trim to ~50 lines. Move merge logic to `skills/01-ingest.md` § Process.
- **Concrete steps:**
  1. Move the merge code block (lines 47-63) into `skills/01-ingest.md` § Process step 3.
  2. Add "Tool allowlist current vs target" section (above) to the agent spec.
  3. (Future, Large) Implement `agents/ingestor/.claude/settings.json` for runtime enforcement.

## Source files (for traceability)

- `agents/ingestor/AGENT.md` — runtime prompt (canonical)
- `schemas/01_ingest.json` — the contract
- `tools/fetch_input.py` — `fetch`, `input_id_for`, `move_to_processed`
- `tools/artifact_io.py` — `write_artifact`, `write_meta`, `build_meta`
- `AGENTS.md` invariant #6 — research first
- `agents/orchestrator/AGENT.md:51-55` — inbound handoff template
