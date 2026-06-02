# Agent 08 — Formatter

## Identity

| Field | Value |
|---|---|
| Tag | `format` |
| hcom target | `@research-pipeline-claude-7` |
| Folder | `agents/formatter/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Compose the final research-report artifact at `05_format/v1.json` (machine-readable) + `v1.md` (human-readable Markdown). Then finalize the manifest. |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 11 Goal-Setting (the final report) |
| Claude Code book chapters | Ch. 4 Multi-Agent Orchestration |

## Capabilities

### Skills owned
- `skills/05-format.md` — the format skill (the only stage this agent owns, plus manifest finalization)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | Write `v1.json` + `v1.md` + `v1.meta.json` | Owns `05_format/` writes |
| `Bash(uv run python -m tools.manifest finalize ...)` | Set `manifest.completed_at` after critic pass | Owns the finalization step |
| `Bash(uv run python -m tools.manifest record_attempt ...)` | Record the format attempt | Audit trail |
| `Read` | Read `AGENTS.md`, `schemas/05_format.json`, `04_synthesize/v1.json`, `02_extract/v1.json`, `03_analyze/v1.json` | Boot + read upstreams |

### Tools explicitly denied
- `WebSearch`, `WebFetch` — researcher only
- `Edit` of any other stage folder (read-only on 01-04 per AGENT.md:95)
- `Bash(uv run python -m tools.validator ...)` — critic only
- `Bash(hcom ...)` except post-write + post-finalize pings
- `Bash(uv run python -m tools.manifest init_manifest ...)` — orchestrator's job

## Constraints

### Input contract
- hcom message from `@orch` with `input_id`
- Reads 3 upstream artifacts (per `agents/formatter/AGENT.md:13-15`):
  - `outputs/<input_id>/04_synthesize/v1.json`
  - `outputs/<input_id>/02_extract/v1.json`
  - `outputs/<input_id>/03_analyze/v1.json`

### Output contract
- Writes only:
  - `outputs/<input_id>/05_format/v1.json` (matches `schemas/05_format.json`)
  - `outputs/<input_id>/05_format/v1.md` (human Markdown, template at `agents/formatter/AGENT.md:33-88`)
  - `outputs/<input_id>/05_format/v1.meta.json` (producer meta, `validation: pending`)
- After critic pass: calls `tools.manifest.finalize(input_id)` which sets `manifest.completed_at`

### Hard rules (NEVER)
- You do not invent content. Everything in the report must trace back to one of the upstream artifacts. (`agents/formatter/AGENT.md:93`)
- You do not edit upstream artifacts. Read-only on 01-04. (`:94`)
- You do not validate. Critic does. (`:95`)
- The Markdown render is for humans. The JSON is for downstream tools. They must agree on the data (Markdown can have nicer prose, but no new facts). (`:96-97`)
- `manifest.json` is the LAST thing you write. If the critic fails this stage, you do NOT call finalize. (`:98`)

## State

### Reads at session start
- `AGENTS.md` — file ownership (you write `05_format/` + top-level `manifest.json`)
- `schemas/05_format.json` — required output structure
- `outputs/<input_id>/04_synthesize/v1.json` — main input
- `outputs/<input_id>/02_extract/v1.json` — for entities + facts
- `outputs/<input_id>/03_analyze/v1.json` — for themes/gaps/contradictions
- `tools/artifact_io.py` — write helpers
- `tools/manifest.py` — finalize, record_attempt

### Writes during session
- `outputs/<id>/05_format/v1.json`
- `outputs/<id>/05_format/v1.md`
- `outputs/<id>/05_format/v1.meta.json`
- After critic pass: `outputs/<id>/manifest.json` via `finalize(input_id)` (sets `completed_at`)

### Persistence
- None beyond the artifact. The manifest update is the persistent record.

## Communication

### Inbound handoffs
- One hcom message from `@orch`: `format: <input_id>`
- The orchestrator's handoff template is at `agents/orchestrator/AGENT.md:78-82`

### Outbound handoffs
- One hcom message to `@critic`: `validate: <input_id> 05_format`
- After critic pass + finalize: report `done: <input_id>` to `@orch`

### Failure modes
- **Missing upstream artifact** → halt. Do not produce a partial report. Tell @orch which stage failed. (`agents/formatter/AGENT.md:108`)
- **Title is empty** → use the first 80 chars of summary as the H1. (`:109`)
- **Mermaid code missing ```mermaid wrapper** → formatter adds the wrapper when rendering (per `scripts/smoke_v2.py:173`)

## Self-verification

- [ ] `v1.json` matches `schemas/05_format.json` (required: `summary`, `entities`, `facts`, `analysis`, `insights`, `references`, `diagrams`, `theses`)
- [ ] `summary` ← `04_synthesize.summary` (verbatim, may lightly polish)
- [ ] `entities` ← `02_extract.entities` (deduped by name)
- [ ] `facts` ← `02_extract.facts` (top 10-20 by confidence)
- [ ] `analysis.themes` ← `03_analyze.themes[].name` (one-line each)
- [ ] `analysis.gaps` ← `03_analyze.gaps[].description`
- [ ] `analysis.contradictions` ← `03_analyze.contradictions[].explanation`
- [ ] `insights` ← `04_synthesize.insights[].insight`
- [ ] `diagrams` ← `04_synthesize.diagrams` (verbatim, no transformation)
- [ ] `theses` ← `04_synthesize.theses` (verbatim)
- [ ] `references` ← `01_ingest` source_ref + cited URLs
- [ ] `v1.md` is the canonical Markdown template (per `agents/formatter/AGENT.md:33-88`); JSON ↔ Markdown agree
- [ ] Mermaid blocks in `v1.md` include the ```` ```mermaid ```` wrapper (the wrapper is added HERE, not in `04_synthesize.diagrams[].code`)
- [ ] `v1.meta.json` has `producer: "formatter"` and `validation.status: "pending"`
- [ ] After critic pass: `tools.manifest.finalize(input_id)` is called
- See `skills/05-format.md` for the full pre-submit checklist + Markdown template.

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `Bash(uv run python -m tools.artifact_io ...)` | implied | allowed | Write `v1.json` + `v1.md` + `v1.meta.json` |
| `Bash(uv run python -m tools.manifest finalize ...)` | implied | allowed | Set `completed_at` after critic pass |
| `Bash(uv run python -m tools.manifest record_attempt ...)` | implied | allowed | Audit trail |
| `Read` | allowed | allowed | Boot + read upstreams |
| `WebSearch`, `WebFetch` | allowed by default | denied | Researcher only |
| `Edit` of `05_format/v1.*` | allowed by default | allowed | Owns its stage |
| `Edit` of `manifest.json` | implied | denied (only via `finalize`) | Atomicity guarantee |
| `Edit` of any other `v1.*` (01-04) | allowed by default | denied | Read-only on upstreams (AGENT.md:95) |
| `Bash(hcom ...)` (except post-write) | allowed by default | denied | Orchestrator-driven |
| `Bash(uv run python -m tools.validator ...)` | allowed by default | denied | Critic only |
| `Bash(uv run python -m tools.manifest init_manifest ...)` | allowed by default | denied | Orchestrator's job |

## Refactor delta

- **Scope:** Small/Medium
- **Current state:** 110-line `agents/formatter/AGENT.md` with the full Markdown template inlined (L33-88) and the field-mapping inlined (L21-31).
- **Target state:** Move the field-mapping to `skills/05-format.md` § Process. Move the Markdown template to `skills/05-format.md` § Output schema (or a sibling `templates/05-format-v1-md.md`).
- **Concrete steps:**
  1. Move the Markdown template (`:33-88`) to `skills/05-format.md` § Output schema (Markdown variant) and/or a new `templates/05-format-v1-md.md`.
  2. Move the field-mapping (`:21-31`) to `skills/05-format.md` § Process step 2.
  3. Add "Tool allowlist current vs target" section (above) to the agent spec.
  4. (Future, Large) Implement `agents/formatter/.claude/settings.json` to enforce the read-only-on-upstreams rule.

## Source files (for traceability)

- `agents/formatter/AGENT.md` — runtime prompt (canonical)
- `schemas/05_format.json` — the contract
- `tools/artifact_io.py` — `write_artifact`, `write_meta`
- `tools/manifest.py` — `finalize`, `record_attempt`
- `AGENTS.md` invariant #5 — manifest is audit trail
- `agents/orchestrator/AGENT.md:78-82` — inbound handoff template
- `scripts/smoke_v2.py:147-188` — `render_md()` for the Markdown template
