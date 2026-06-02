# CLAUDE.md

This repo is designed for Claude Code and agentic workflows.

## Read First

1. Read `AGENTS.md` for current team memory and invariants.
2. Read `agentic/policies/approval-gates.md` before using tools that write, delete, send, publish, or mutate external state.
3. Read the relevant `.claude/agents/*.md` or `.claude/skills/*/SKILL.md` before using a specialized role or workflow.

## Operating Rules

- Do not silently overwrite files.
- Do not read secrets unless the task explicitly requires approved secret handling.
- Do not run destructive commands without explicit approval.
- Keep durable facts in `agentic/knowledge/`.
- Stage memory candidates in `agentic/memory/` with source and validation status.
- Run the relevant gate in `scripts/gates/` before reporting completion.

## Common Commands

```cmd
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py
python scripts\gates\scan_secrets.py
```

If a command is not present yet, report the missing gate in the validation report instead of inventing a pass.

