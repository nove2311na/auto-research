# Agent 02 — Researcher

## Identity

| Field | Value |
|---|---|
| Tag | `research` |
| hcom target | `@research-pipeline-claude-8` |
| Folder | `agents/researcher/` |
| Lifecycle | per-handoff (one Claude session per input) |
| Purpose | Iterative `WebSearch` + `WebFetch` rounds on the input subject → research dossier at `outputs/<input_id>/00_research/v1.json`. |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 14 RAG, Ch. 18 Guardrails (depth-bounded) |
| Claude Code book chapters | Ch. 5 MCP, Ch. 8 Prompt Craft |

## Capabilities

### Skills owned
- `skills/00-research.md` — research dossier (the only stage this agent owns)

### Tools allowed (least-privilege)

| Tool | Purpose | Justification |
|---|---|---|
| `Bash(uv run python -m tools.fetch_input ...)` | Resolve `input_ref` → text + meta | To extract subject from non-topic inputs |
| `Bash(uv run python -m tools.artifact_io ...)` | Write dossier + meta | Owns `00_research/` writes |
| `WebSearch` | Iterative queries per depth table | Explicit in `agents/researcher/AGENT.md:7,76` |
| `WebFetch` | Pull full page content for each URL | Explicit in `agents/researcher/AGENT.md:7,76` |
| `Read` | Read schemas, `AGENTS.md`, `learnings.md` | Standard agent boot |
| `Grep`, `Glob` | Locate files in `outputs/00_research/` | Self-check before writing |

### Tools explicitly denied
- `Bash(hcom ...)` except for the post-write `@critic` ping (orchestrator-driven; researcher is on the receiving end)
- `Edit` of any `v1.*` artifact other than its own `00_research/v1.json`
- `Edit` of any other stage folder (`01_ingest`, `02_extract`, etc.)
- `Bash(uv run python -m tools.validator ...)` — critic only
- `Bash(uv run python -m tools.manifest ...)` — orchestrator/critic/formatter only
- `Write` of `prd.json` or `progress.md` — orchestrator only

## Constraints

### Input contract
- hcom message from `@orch` with: `input_id`, `input_ref` (path/URL/topic), `depth` (one of `shallow`/`medium`/`deep`)
- Per `agents/researcher/AGENT.md:21-32`, the `depth` flag controls rounds / queries / sources cap:
  - `shallow`: 1 round, 3 queries, ≤5 sources
  - `medium` (default): 2 rounds, 5 queries/round, ≤10 sources
  - `deep`: 3 rounds, ~3-5 unique queries/round, ≤15 sources

### Output contract
- Writes only:
  - `outputs/<input_id>/00_research/v1.json` — the dossier
  - `outputs/<input_id>/00_research/v1.meta.json` — producer meta (`validation: pending`)
- Schema: `schemas/00_research.json` (required: `topic`, `depth`, `queries`, `sources`, `synthesis`)

### Hard rules (NEVER)
- You do not edit another agent's stage folder. You write only to `outputs/<input_id>/00_research/`. (`agents/researcher/AGENT.md:70`)
- You do not self-validate. The critic decides pass/fail. (`:72`)
- You always write `v1.meta.json` even if research was trivial (e.g. shallow depth, 1 query, 1 source). (`:73`)
- Source dedup is by URL only. Do NOT re-fetch the same URL twice across rounds. (`:75`)
- You are a Claude session with `WebSearch` and `WebFetch` — use them. Do not try to read from local files for research; the dossier is a web-research artifact. (`:76`)
- Inline citations in `synthesis` are `[N]` where N is the 1-based index into `sources[]`. Every cited number must resolve to an existing source. (`:79-80`)

## State

### Reads at session start
- `AGENTS.md` — file ownership (you write only to `00_research/`)
- `schemas/00_research.json` — the contract
- `tools/artifact_io.py` — `build_meta`, `write_meta`, `write_artifact`, `next_version`
- `tools/fetch_input.py` — `fetch()` for resolving the input ref
- `learnings.md` — accumulated knowledge from prior runs

### Writes during session
- `outputs/<id>/00_research/v1.json` (dossier)
- `outputs/<id>/00_research/v1.meta.json` (meta)

### Persistence
- None (the dossier is the persistent artifact; the researcher's working memory is the dossier itself + the source URLs fetched so far)

## Communication

### Inbound handoffs
- One hcom message from `@orch`: `research: <input_id> depth=<X>` with `<input_ref>` in the description
- The orchestrator's handoff template is at `agents/orchestrator/AGENT.md:44-49`

### Outbound handoffs
- One hcom message to `@critic`: `validate: <input_id> 00_research`
- Then wait idle for orchestrator's next handoff

### Failure modes
- **WebSearch returns 0 results** → record the query with `results_count: 0`, try a reformulation, note in `gaps`. (`agents/researcher/AGENT.md:97-99`)
- **WebFetch times out / 4xx / 5xx** → skip that URL, retry ≤1, note in `gaps` if it was a key source. (`:100`)
- **Topic is ambiguous** (e.g. "transformers") → pick most likely subject from search-result context, record disambiguation in `gaps`. (`:101-103`)
- **All sources are low-quality** (SEO spam) → still produce the dossier; flag source-quality concern in `gaps`. (`:104-105`)

## Self-verification

- [ ] `topic` is one sentence, specific (not "AI" — "the current state of open-weights LLM safety research as of 2026") per `agents/researcher/AGENT.md:84-86`
- [ ] Round 1 queries are diverse (not 5 variants of the same phrase) per `:87`
- [ ] Sources weighted toward primary/authoritative; `relevance: high` only for actually-cited sources per `:88-89`
- [ ] `synthesis` is one piece of writing (not stapled per-source paragraphs) per `:90-91`
- [ ] `gaps` are honest (no pretending coverage was complete) per `:92-93`
- [ ] All `[N]` citations in `synthesis` resolve to `sources[]` indices
- [ ] `v1.meta.json` written even for shallow / 1-source case
- See `skills/00-research.md` for the full pre-submit checklist.

## Tool allowlist — current vs target

| Tool | Current | Target (least-privilege) | Justification |
|---|---|---|---|
| `WebSearch` | allowed | allowed | Core research tool |
| `WebFetch` | allowed | allowed | Core research tool |
| `Bash(uv run python -m tools.fetch_input ...)` | implied | allowed | Resolve `input_ref` |
| `Bash(uv run python -m tools.artifact_io ...)` | implied | allowed | Write dossier + meta |
| `Read` | allowed | allowed | Boot read |
| `Grep`, `Glob` | implied | allowed | Self-check |
| `Edit` of `00_research/v1.*` | allowed by default | allowed | Owns its stage |
| `Edit` of any other `v1.*` | allowed by default | denied | Cross-stage write forbidden by AGENT.md:70 |
| `Bash(hcom ...)` (except post-write ping) | allowed by default | denied | Orchestrator-driven; agent only responds |
| `Bash(uv run python -m tools.validator ...)` | allowed by default | denied | Critic only (AGENT.md:72) |
| `Bash(uv run python -m tools.manifest ...)` | allowed by default | denied | Not its concern |
| `Write` to `prd.json` or `progress.md` | allowed by default | denied | Orchestrator only |

## Refactor delta

- **Scope:** Small
- **Current state:** 106-line `agents/researcher/AGENT.md` with 12-step process inlined. WebSearch/WebFetch enumerated at lines 7, 76.
- **Target state:** Trim to ~60 lines (boot read + process overview + hard rules). Move the 12-step process to `skills/00-research.md` § Process.
- **Concrete steps:**
  1. Move steps 2-11 (`agents/researcher/AGENT.md:23-63`) into `skills/00-research.md` § Process.
  2. Keep steps 1 + 12 in the AGENT.md (the handoff-summary and the post-write ping).
  3. Add an explicit "Tool allowlist current vs target" section (above) and document the proposed tightening.
  4. (Future, Large) Implement `agents/researcher/.claude/settings.json` to enforce the allowlist.

## Source files (for traceability)

- `agents/researcher/AGENT.md` — runtime prompt (canonical)
- `schemas/00_research.json` — the contract
- `tools/artifact_io.py` — `build_meta`, `write_meta`, `write_artifact`
- `tools/fetch_input.py` — `fetch`, `input_id_for`
- `AGENTS.md` invariant #6 — "Research stage runs first, always"
- `agents/orchestrator/AGENT.md:44-49` — inbound handoff template
