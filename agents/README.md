# Agent Prompt Compatibility Layer

Runtime agent specs live in `.claude/agents/`.

This folder exists so older docs that reference `agents/<role>/AGENT.md` do not point at missing paths. Do not edit these shims for runtime behavior; edit the corresponding `.claude/agents/<role>.md` and `.claude/agents/<role>.json` files instead.

| Legacy path | Runtime source |
|---|---|
| `agents/orchestrator/AGENT.md` | `.claude/agents/orchestrator.md` |
| `agents/researcher/AGENT.md` | `.claude/agents/researcher.md` |
| `agents/ingestor/AGENT.md` | `.claude/agents/ingestor.md` |
| `agents/extractor/AGENT.md` | `.claude/agents/extractor.md` |
| `agents/analyzer/AGENT.md` | `.claude/agents/analyzer.md` |
| `agents/synthesizer/AGENT.md` | `.claude/agents/synthesizer.md` |
| `agents/critic/AGENT.md` | `.claude/agents/critic.md` |
| `agents/formatter/AGENT.md` | `.claude/agents/formatter.md` |

