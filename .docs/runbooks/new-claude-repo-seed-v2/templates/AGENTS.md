# AGENTS.md

Keep this file concise. Archive older notes into `agentic/memory/archive/` when it grows beyond 200 lines.

## What This Repo Is

This repo contains a Claude Code-native agentic system. It uses specialized agents, reusable skills, explicit tool policies, and deterministic gates to turn user goals into validated artifacts.

## Hard Invariants

1. `CLAUDE.md` is the entrypoint, not the full knowledge base.
2. `.claude/agents/` contains bounded roles with allowed tools and forbidden actions.
3. `.claude/skills/` contains reusable procedures with progressive disclosure.
4. `agentic/knowledge/` stores durable project knowledge.
5. `agentic/memory/` stores memory candidates and approved memory cards.
6. `agentic/policies/` defines approval and risk rules.
7. `scripts/gates/` contains deterministic validation.
8. Generated work is versioned or create-only unless a human approves merge.

## Current Agent Team

| Agent | Role | Default Access |
|---|---|---|
| `idea-harvester` | Normalize vague intent into seed input. | read/search |
| `reference-harvester` | Distill source patterns. | read/search/web when approved |
| `system-architect` | Produce agent system specs. | read/write specs |
| `scaffold-planner` | Plan file creation and validation. | read/write plans |
| `gatekeeper` | Validate outputs and report risks. | read/run gates |

## Memory Promotion

Promote a memory only when it has:

- source,
- date,
- owner,
- validation status,
- reason it should persist.

