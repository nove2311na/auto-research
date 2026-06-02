# Template — Agent Spec

> **Use this template for every `agents/NN-<role>.md` file in `.docs/agentic/agents/`.**
> Sections marked `[required]` must be present. Sections marked `[recommended]` may be omitted only with justification. Sections marked `[optional]` are at author discretion.

## Identity `[required]`

| Field | Value |
|---|---|
| Tag | (e.g. `research`) |
| hcom target | (e.g. `@research-pipeline-claude-8`) |
| Folder | `agents/<role>/` |
| Lifecycle | (per-handoff / persistent / singleton) |
| Purpose | (1 sentence — what this agent does) |
| Antonio Gulli patterns | (list applicable pattern names from Ch. 7 Multi-Agent, Ch. 16 Reasoning, Ch. 18 Guardrails, etc.) |

## Capabilities `[required]`

### Skills owned
- (list of `skills/NN-*.md` this agent owns)

### Tools allowed (least-privilege)
| Tool | Purpose | Justification |
|---|---|---|
| (e.g. `Bash(uv run python ...)`) | (1 line) | (why this tool is needed) |
| ... | ... | ... |

### Tools explicitly denied
- (e.g. `WebSearch` — out of scope for this role)
- (e.g. `Edit` of any file outside this agent's `outputs/<id>/<role>/`)

## Constraints `[required]`

### Input contract
- (what this agent MUST receive to start a handoff; cite the hcom message template + relevant schema)

### Output contract
- (where this agent MUST write; cite the schema file)
- (e.g. "writes `outputs/<id>/<stage>/v1.json` + `v1.meta.json` via `tools.artifact_io.write_artifact` + `write_meta`")

### Hard rules (NEVER)
- (imperative bullets; cite source: `AGENTS.md` invariants, `agents/<role>/AGENT.md` "Hard rules" section, or `python.md` "Hard invariants")

## State `[required]`

### Reads at session start
- (file paths this agent must read before acting)

### Writes during session
- (file paths this agent writes; distinguish "owned" vs "auxiliary" — e.g. orchestrator owns `prd.json` + `progress.md` but does not own `v1.*`)

### Persistence
- (state-on-disk vs in-memory; reference the "Ralph Wiggum loop" pattern from `AGENTS.md`)

## Communication `[required]`

### Inbound handoffs
- (hcom messages this agent expects to receive; cite `agents/orchestrator/AGENT.md` handoff templates)

### Outbound handoffs
- (hcom messages this agent sends; e.g. ping `@critic` after writing artifact)

### Failure modes
- (what this agent does on timeout, on missing input, on schema violation, etc.)

## Self-verification `[recommended]`

- (numbered pre-submit checklist; cross-link to the relevant `skills/NN-*.md` checklist)

## Refactor delta `[required]`

- **Scope:** (Small / Medium / Large)
- **Current state:** (1-2 sentences — what exists today in `agents/<role>/AGENT.md`)
- **Target state:** (1-2 sentences — what the file should look like post-refactor)
- **Concrete steps:**
  1. ...
  2. ...

## Source files (for traceability)

- (every claim in this spec must trace to one of these)
- `agents/<role>/AGENT.md` — runtime prompt (canonical)
- `AGENTS.md` — team invariants
- (etc.)

---

**Authoring tips:**
- **Concrete over abstract.** Don't write "manages state"; write "writes `prd.json.current_input_id` and `prd.json.current_stage` per `agents/orchestrator/AGENT.md:92-101`".
- **Cite line numbers** when referencing source code. The user values precision.
- **Tables over prose** for tool allowlists, identity, and refactor deltas.
- **NEVER blocks** in the constraints section should match the wording of the source invariant 1:1 where possible.
