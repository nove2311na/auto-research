# Patterns Applied — Antonio Gulli Traceability

> **Source:** `Agentic_Design_Patterns.pdf` (Antonio Gulli, 424 pages, 21 patterns in 4 parts).
> **Source:** `Claude Code The Definitive Guide to Agentic Development.pdf` (12 chapters, 2026).
>
> This file traces every spec in `.docs/agentic/` back to the patterns and chapters that informed it. If a spec is changed, update this file to keep the trace accurate.

## Pattern index (Gulli)

| Ch. | Pattern | Part | Used in |
|---|---|---|---|
| 1 | Prompt Chaining | Foundations | (not directly — pipeline is staged, not chained-in-prompt) |
| 2 | Routing | Foundations | `agents/01-orchestrator.md` (orchestrator routes by stage) |
| 3 | Parallelization | Foundations | `skills/02-extract.md` (3 parallel options A/B/C) |
| 4 | Reflection | Foundations | (implicit: critic's LLM-judge is a form of reflection; `validation/03-llm-judge.md`) |
| 5 | Tool Use | Foundations | `skills/*.md` (every skill uses tools) |
| 6 | Planning | Foundations | `agents/01-orchestrator.md` (drives 6-stage plan) |
| 7 | **Multi-Agent** | Foundations | **`agents/*.md` (8 agents, all 8 specs)** |
| 8 | Memory | Foundations | `agents/01-orchestrator.md` (state on disk), `AGENTS.md` (team memory) |
| 9 | Learning | Foundations | (V2 — not yet implemented; `learnings.md` is the seed) |
| 10 | **MCP** | Foundations | **`skills/*.md` (input_schema as a structured contract, like MCP tool schemas)** |
| 11 | Goal-Setting | Foundations | `agents/01-orchestrator.md` (the "done" definition is the goal) |
| 12 | Exception Handling | Part 2 | `skills/*.md` (failure modes sections), `validation/05-drift-detection.md` |
| 13 | HITL (Human-in-the-Loop) | Part 2 | (V1 minimal: only the orchestrator's "escalate to human" failure mode) |
| 14 | RAG | Part 2 | `agents/02-researcher.md`, `skills/00-research.md` (WebSearch+WebFetch is the RAG step) |
| 15 | **A2A** (Inter-Agent Communication) | Part 2 | **`agents/01-orchestrator.md` (hcom handoff protocol)** |
| 16 | **Reasoning Techniques** | Part 2 | **`agents/01-orchestrator.md` (decompose refactor into atomic steps)** |
| 17 | Resource-Aware Optimization | Part 3 | `validation/04-smoke-tests.md` (<5s smoke tests per `python.md`) |
| 18 | **Guardrails / Safety** | Part 3 | **`agents/*.md` (tool allowlists, hard rules), `validation/*.md`** |
| 19 | **Evaluation & Monitoring** | Part 3 | **`validation/*.md` (all 5 specs)** |
| 20 | Prioritization | Part 3 | `refactor-plan.md` (phase ordering) |
| 21 | Exploration | Part 3 | (V2 — not yet implemented) |

## Per-spec traceability

### Agent specs

| Spec | Antonio Gulli patterns | Claude Code book chapters |
|---|---|---|
| `agents/01-orchestrator.md` | Ch. 2 Routing, Ch. 6 Planning, Ch. 7 Multi-Agent, Ch. 8 Memory, Ch. 11 Goal-Setting, Ch. 15 A2A, Ch. 16 Reasoning | Ch. 2 Permission Architecture, Ch. 4 Multi-Agent Orchestration, Ch. 10 Failure Modes |
| `agents/02-researcher.md` | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 14 RAG, Ch. 18 Guardrails (depth-bounded) | Ch. 5 MCP, Ch. 8 Prompt Craft |
| `agents/03-ingestor.md` | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 10 MCP (dispatch by file type), Ch. 18 Guardrails | Ch. 4 Multi-Agent Orchestration |
| `agents/04-extractor.md` | Ch. 3 Parallelization, Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 18 Guardrails | Ch. 4 Multi-Agent Orchestration, Ch. 8 Prompt Craft |
| `agents/05-analyzer.md` | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 12 Exception Handling (gaps + contradictions) | Ch. 4 Multi-Agent Orchestration |
| `agents/06-synthesizer.md` | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 16 Reasoning (narrative + theses), Ch. 18 Guardrails (≥2 diagrams + ≥2 theses) | Ch. 4 Multi-Agent Orchestration, Ch. 8 Prompt Craft |
| `agents/07-critic.md` | Ch. 4 Reflection, Ch. 7 Multi-Agent, Ch. 18 Guardrails, **Ch. 19 Evaluation & Monitoring** | Ch. 10 Failure Modes, Ch. 12 Team Adoption |
| `agents/08-formatter.md` | Ch. 5 Tool Use, Ch. 7 Multi-Agent, Ch. 11 Goal-Setting (the final report) | Ch. 4 Multi-Agent Orchestration |

### Skill specs

| Spec | Antonio Gulli patterns | Claude Code book chapters |
|---|---|---|
| `skills/00-research.md` | Ch. 5 Tool Use, Ch. 10 MCP, Ch. 14 RAG | Ch. 5 MCP, Ch. 8 Prompt Craft |
| `skills/01-ingest.md` | Ch. 5 Tool Use, Ch. 10 MCP (file-type dispatch) | Ch. 5 MCP |
| `skills/02-extract.md` | Ch. 3 Parallelization, Ch. 5 Tool Use, Ch. 10 MCP | Ch. 5 MCP, Ch. 8 Prompt Craft |
| `skills/03-analyze.md` | Ch. 5 Tool Use, Ch. 12 Exception Handling | Ch. 8 Prompt Craft |
| `skills/04-synthesize.md` | Ch. 5 Tool Use, Ch. 16 Reasoning (narrative), Ch. 18 Guardrails (min-items) | Ch. 3 Context Engineering, Ch. 8 Prompt Craft |
| `skills/05-format.md` | Ch. 5 Tool Use, Ch. 11 Goal-Setting | Ch. 4 Multi-Agent Orchestration |
| `skills/06-validate.md` | Ch. 4 Reflection, Ch. 18 Guardrails, Ch. 19 Evaluation & Monitoring | Ch. 10 Failure Modes |

### Validation specs

| Spec | Antonio Gulli patterns | Claude Code book chapters |
|---|---|---|
| `validation/01-pre-execution-schema.md` | Ch. 18 Guardrails, Ch. 19 Evaluation & Monitoring | Ch. 2 Permission Architecture, Ch. 10 Failure Modes |
| `validation/02-post-execution-completeness.md` | Ch. 18 Guardrails, Ch. 19 Evaluation & Monitoring | Ch. 10 Failure Modes |
| `validation/03-llm-judge.md` | Ch. 4 Reflection, Ch. 18 Guardrails, Ch. 19 Evaluation & Monitoring | Ch. 10 Failure Modes, Ch. 12 Team Adoption |
| `validation/04-smoke-tests.md` | Ch. 17 Resource-Aware Optimization, Ch. 19 Evaluation & Monitoring | Ch. 11 CI/CD & Headless Automation |
| `validation/05-drift-detection.md` | Ch. 12 Exception Handling, Ch. 19 Evaluation & Monitoring | Ch. 10 Failure Modes, Ch. 11 CI/CD & Headless Automation |

## Coverage check

For each of the 21 Gulli patterns:

- **Directly applied:** 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20 — 16 patterns
- **Implicit / future:** 1, 2, 9, 13, 21 — 5 patterns
  - 1 (Prompt Chaining) — could be applied in synthesizer's narrative
  - 2 (Routing) — partially via orchestrator; full routing table is V2
  - 9 (Learning) — `learnings.md` exists but is not yet integrated into prompts; V2
  - 13 (HITL) — minimal in V1; full review queue is V2
  - 21 (Exploration) — out of scope

## Claude Code book chapter index

| Ch. | Title | Used in |
|---|---|---|
| 1 | Beyond the Getting-Started Guide | (general) |
| 2 | **Permission and Trust Architecture** | **`agents/*.md` (allowlist), `validation/01-pre-execution-schema.md`** |
| 3 | **Context Engineering** | **`agents/01-orchestrator.md` (send only upstream artifact), `skills/04-synthesize.md`** |
| 4 | **Multi-Agent Orchestration** | **`agents/01-orchestrator.md`, all `agents/*.md`** |
| 5 | **MCP** | **`skills/*.md` (input_schema as tool contract)** |
| 6 | CI/CD & Headless Automation | `validation/04-smoke-tests.md`, `validation/05-drift-detection.md` |
| 7 | IDE Integration | (n/a for this repo) |
| 8 | **Prompt Craft for Agentic Tools** | **`agents/*.md`, `skills/*.md`** |
| 9 | Large and Legacy Codebases | (n/a — greenfield repo) |
| 10 | **Failure Modes and Recovery** | **`agents/01-orchestrator.md`, `agents/07-critic.md`, all `validation/*.md`** |
| 11 | (extended team patterns) | `AGENTS.md`, `learnings.md`, `progress.md` |
| 12 | Team Adoption Patterns + Economics | `refactor-plan.md` (phase ordering), `agents/07-critic.md` (LLM-judge rubric) |

## Maintenance

When a new spec is added, add a row to the relevant traceability table. When a spec is changed in a way that changes which pattern it implements, update the row.

When a new pattern is applied (e.g. V2 introduces Learning, HITL, or MCP for real), update the "Coverage check" section.
