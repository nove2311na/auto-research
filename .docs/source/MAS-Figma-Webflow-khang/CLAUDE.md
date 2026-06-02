# CLAUDE.md

This folder is a Claude Code-native agentic workspace for the MAS V3 Figma-to-Webflow workflow.

## Read First

1. Read `agentic/memory/team-memory.md` for the current agent team, invariants, and operating boundaries.
2. Read `agentic/policies/runtime-instructions.md` for the MAS V3 mandates adapted to Claude Code.
3. Read `agentic/orchestration/sop.md` before starting any Figma-to-Webflow run.
4. Read `agentic/specs/agent-system-spec.md` for the standalone agent-system contract.
5. Read `agentic/orchestration/reflection-loop.md` and `agentic/orchestration/phase-state-machine.md` before closing or changing phases.
6. Read `agentic/policies/approval-gates.md` before using Webflow, Figma, file writes, archive/restore, or any external connector.

## Common Commands

```cmd
python scripts\init_workspace.py --project "Project Name" --figma "https://www.figma.com/design/file"
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py --target .
python scripts\gates\scan_secrets.py --target .
python scripts\gates\validate_agent_system_spec.py --target .
python scripts\gates\validate_skills.py --target .
python scripts\gates\validate_workspace_artifacts.py --target .
python scripts\gates\validate_phase_state.py --target .
python scripts\gates\validate_relative_paths.py --target .
```

Workspace lifecycle:

```cmd
python scripts\archive_workspace.py
python scripts\restore_workspace.py
python scripts\restore_workspace.py 0
```

## Operating Rules

- Never silently overwrite existing files.
- Never delete or restore `workspace/` unless the archive/restore safety gates pass.
- Never proceed from Blueprint to Webflow build until the user approves.
- Never use `whtml_builder`; build with Webflow native element operations and MCP-352.
- Always use REM units for spacing, sizes, and typography.
- Always record evidence in workspace JSON files before reporting progress.
- Always record Webflow actions with reason, action, observation, and next decision.
- Always run QA from real Webflow state or snapshots; do not guess visual parity.
- Treat `agentic/evals/standalone-architecture-baseline.md` as the local architecture baseline.
- Use `knowledge-base/client-first-class-map.json` before mapping Figma properties to Webflow classes.
- Use Python as the project automation language.
- Keep local filesystem references relative inside this folder.

## Workflow Summary

1. `@pm` receives the user request and checks `agentic/memory/session-handoff.md`, `agentic/orchestration/sop.md`, and workspace state.
2. `@operator` extracts Figma/raw data into `workspace/rawdata/` and `workspace/contents/`.
3. `@architect` produces Client-First blueprints in `workspace/blueprints/`.
4. `@pm` presents the blueprint and stops for approval.
5. `@operator` builds in Webflow using MCP-352.
6. `@gatekeeper` or `@architect` runs reflection review on risky artifacts.
7. `@architect` runs QA against actual Webflow state and records fixes.
8. `@pm` updates `agentic/memory/session-handoff.md` and reports evidence-backed completion.
