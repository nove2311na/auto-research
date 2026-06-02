# Agent Inventory — 8 Agents

This folder contains the formal spec for each of the 8 agents in the research-pipeline swarm. See `../README.md` for the overall spec structure and `../refactor-plan.md` for the gap analysis.

## Overview

| # | Tag | hcom target | Folder | Owns | Spec |
|---|---|---|---|---|---|
| 1 | `orch` | `@research-pipeline-claude-1` | `agents/orchestrator/` | (none — routes) | [01-orchestrator.md](01-orchestrator.md) |
| 2 | `research` | `@research-pipeline-claude-8` | `agents/researcher/` | `00_research` | [02-researcher.md](02-researcher.md) |
| 3 | `ingest` | `@research-pipeline-claude-2` | `agents/ingestor/` | `01_ingest` | [03-ingestor.md](03-ingestor.md) |
| 4 | `extract` | `@research-pipeline-claude-3` | `agents/extractor/` | `02_extract` | [04-extractor.md](04-extractor.md) |
| 5 | `analyze` | `@research-pipeline-claude-4` | `agents/analyzer/` | `03_analyze` | [05-analyzer.md](05-analyzer.md) |
| 6 | `synth` | `@research-pipeline-claude-5` | `agents/synthesizer/` | `04_synthesize` | [06-synthesizer.md](06-synthesizer.md) |
| 7 | `critic` | `@research-pipeline-claude-6` | `agents/critic/` | (validates all) | [07-critic.md](07-critic.md) |
| 8 | `format` | `@research-pipeline-claude-7` | `agents/formatter/` | `05_format` | [08-formatter.md](08-formatter.md) |

## Tool-allowlist delta (proposed)

For each agent, the spec contains a "Tool allowlist — current vs target" table. The summary:

| Agent | Current (implied) | Target (least-privilege) |
|---|---|---|
| `orch` | hcom + Read + Write (state) + Grep/Glob | + explicit denial of `WebSearch`/`WebFetch` and `Edit` of `v1.*` |
| `research` | `WebSearch` + `WebFetch` + Python + Read | + explicit denial of `Edit` of other stages, `Bash(validator)`, `Bash(manifest)` |
| `ingest` | Python + Read + Grep/Glob | + explicit denial of `WebSearch`/`WebFetch`, `Bash(validator)`, `Bash(manifest)` |
| `extract` | Python + Read | + explicit denial of `Bash(validator)`, `Bash(manifest)`, `Bash(pick_winner)`, `Edit` of stage-root |
| `analyze` | Python + Read | + explicit denial of `WebSearch`/`WebFetch`, `Bash(validator)`, `Bash(manifest)` |
| `synth` | Python + Read | + explicit denial of `WebSearch`/`WebFetch`, `Bash(validator)`, `Bash(manifest)` |
| `critic` | Python (`validator`, `artifact_io`, `manifest`) + Read | + explicit denial of `Edit` of content, `WebSearch`/`WebFetch`, `Bash(manifest#init)`, `Bash(manifest#finalize)` |
| `format` | Python (`artifact_io`, `manifest#finalize`) + Read | + explicit denial of `Edit` of upstream 01-04, `WebSearch`/`WebFetch`, `Bash(validator)` |

The implementation of these tightened allowlists (per-agent `agents/<role>/settings.json`) is a follow-up refactor — see `../refactor-plan.md` Phase E.

## Cross-references

- **Skills** (what each agent does): see `../skills/README.md`
- **Validation** (what enforces correctness): see `../validation/README.md`
- **Templates** (the canonical spec shapes): see `../templates/`
- **Source of truth for stage list:** `pipeline.json`
- **Source of truth for team invariants:** `AGENTS.md`
- **Runtime prompts** (canonical for now): `../../agents/<role>/AGENT.md`
