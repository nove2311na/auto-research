# `.docs/agentic/` — Agentic Refactor Spec

This folder is the **target-architecture spec** for restructuring the research-pipeline repo at `G:\My Drive\10_Learning\_Research\auto-research` to follow agentic best practices. It is **reference material for the refactor** — runtime files in `agents/`, `schemas/`, `tools/`, and `scripts/` stay canonical until the refactor is executed.

## Contents

### Reference PDFs (read first)

- `Agentic_Design_Patterns.pdf` — Antonio Gulli, 21 patterns across 4 parts (Foundations → Memory/MCP/Goals → Failure/HITL/RAG → A2A/Reasoning/Guardrails/Eval). The taxonomy anchor for `patterns-applied.md`.
- `Claude Code The Definitive Guide to Agentic Development.pdf` — 12 chapters, focused on Claude Code patterns. Especially relevant: Ch. 2 Permission Architecture, Ch. 3 Context Engineering, Ch. 4 Multi-Agent Orchestration, Ch. 5 MCP, Ch. 8 Prompt Craft, Ch. 10 Failure Modes, Ch. 12 Team Adoption.

### Top-level

- `refactor-plan.md` — current state → target state → gap per deliverable. **Start here.**
- `patterns-applied.md` — traceability table: which Antonio Gulli pattern each spec implements.

### Deliverables

| Folder | What | Count |
|---|---|---|
| `agents/` | Per-agent spec (identity, capabilities, constraints, state, communication, tool allowlist current-vs-target, refactor delta) | 8 |
| `skills/` | Per-skill spec (input_schema, process, output_schema, example, self-check checklist, validation, refactor delta) | 7 |
| `validation/` | Per-validation-surface spec (purpose, how-it-works, pass/fail, how-to-invoke, coverage, refactor delta) | 5 |
| `templates/` | Canonical templates (agent-spec, skill-spec, validation-spec) | 3 |

**Total: 27 new files** (this README + 3 top-level + 8 agents + 7 skills + 5 validation + 3 templates = 24 doc files + this README + 2 patterns-applied + refactor-plan = 27, plus the 2 untouched PDFs).

## How to read this

1. **If you are planning the refactor:** start with `refactor-plan.md`. It enumerates the gap and the concrete steps per deliverable.
2. **If you are reviewing an agent:** read `agents/0N-<role>.md`. Cross-link to the skills it owns and the validation that checks its output.
3. **If you are reviewing a skill:** read `skills/NN-<name>.md`. Cross-link to the schema, the agent that owns it, and the validation that enforces it.
4. **If you are reviewing a validation:** read `validation/NN-<surface>.md`. Cross-link to the runtime tool/script that implements it.
5. **If you are authoring a new spec:** start with the relevant `templates/*.md` file.

## Source-of-truth policy

| Layer | Lives at | Status |
|---|---|---|
| Runtime prompt | `agents/<role>/AGENT.md` | Canonical for runtime. **Do not modify** as part of this deliverable. |
| Machine contract | `schemas/*.json` | Canonical for runtime. |
| Runtime validator | `tools/validator.py`, `tools/manifest.py` | Canonical for runtime. |
| Runtime tests | `scripts/smoke_*.py` | Canonical for runtime. |
| Team memory | `AGENTS.md` | Canonical. |
| Source of truth | `pipeline.json` | Canonical. |
| **NEW: formal spec** | `.docs/agentic/` | **Target-architecture for refactor.** Does not change runtime until refactor is executed. |

When docs and code disagree, **code wins for now** (it's running). The `## Refactor delta` section in each spec lists the concrete changes to migrate code → target.

## Conventions used in the specs

- **Tool allowlist notation:** backticked `Bash(uv run python ...)` for shell patterns; `WebSearch`, `WebFetch`, `Read`, `Write`, `Edit`, `Grep`, `Glob` for Claude tools.
- **Stage ids:** `00_research`, `01_ingest`, `02_extract`, `03_analyze`, `04_synthesize`, `05_format` (per `pipeline.json`).
- **hcom targets:** `@research-pipeline-claude-1` through `@research-pipeline-claude-8` (per `AGENTS.md`).
- **File paths:** `outputs/<input_id>/<stage>/v<N>.<ext>` (backticks).
- **Citations:** inline `[N]` where N is 1-based index into `sources[]` (per `agents/researcher/AGENT.md:79-80`).
- **Score range:** `0.0`–`1.0`; pass threshold default `0.7` (per `pipeline.json` → `critic.llm_judge_threshold`).
- **Confidence / relevance / novelty enums:** `high | medium | low`.
- **Diagram type enum:** `flowchart | sequence | mindmap | graph | class | state | concept`.
- **Input source enum:** `text | file | url | pdf | docx | batch_dir`.
- **Validation status enum:** `pending | pass | fail`.

## Known drift (documented for refactor)

These inconsistencies exist in the current runtime files. They are **out of scope for this spec** (a refactor fix is a separate plan), but documented here for visibility:

- **7 vs 8 agents:** `tools/__init__.py:1` and `pyproject.toml` description say "7 agents"; `AGENTS.md` and `README.md` (post-fix) say "8 agents". Canonical: **8** (orchestrator + researcher + 6 stage agents).
- **5 vs 6 stages:** `scripts/kickoff.sh:17` and `.claude/rules/python.md:41` say "5 stages"; `pipeline.json` and the rest say "6 stages" (with `00_research` added). Canonical: **6**.
- **5 vs 6 hard invariants:** `README.md` lists 5; `AGENTS.md` lists 6 (the 6th is "Research stage runs first, always"). Canonical: **6** (per `AGENTS.md`).
- **`agents/README.md` count:** says "7 Agents" — drift from the canonical 8.

These are tracked in `refactor-plan.md` as Small-scope refactor items.

## Out of scope (V1)

From the runtime repo's own `README.md` §"Out of scope (V1)":

- Multi-language research (search arxiv/web in other languages)
- Cross-input correlation (compare insights across many inputs)
- Persistent memory across runs (knowledge base that grows over time)
- UI layer (web viewer for `outputs/`)
- Custom schemas per-input (one global schema set; per-input override is V2)
- Fine-tuned critic
- Auto-archival of old `outputs/` to S3/cold storage

If the refactor touches any of these, it should be flagged as V2.
