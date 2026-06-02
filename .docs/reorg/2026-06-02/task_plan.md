# Task Plan: Repo Cleanup and Runbook

## Goal
Make the repo easier to navigate without breaking runtime paths used by hcom, scripts, tools, schemas, and Claude agents.

## Constraints
- Do not move runtime directories: `scripts/`, `tools/`, `schemas/`, `.claude/`, `.hcom/`, `outputs/`, `gates/`, `evals/`, `observability/`.
- Do not edit human-owned `pipeline.json`, `AGENTS.md`, or `CLAUDE.md` unless required for operation.
- Keep `.docs/agentic/` because `.claude/agents/*` and `.claude/skills/*` reference it.
- Validate after changes with Python compile, spec validation, and smoke tests.

## Checklist
- [x] Audit current file references.
- [x] Add user-facing pipeline start guide.
- [x] Add `.docs` index.
- [x] Move unreferenced loose audit docs into a reports folder.
- [x] Update stale root README commands and file map.
- [x] Add `agents/<role>/AGENT.md` compatibility shims for legacy references.
- [x] Run validation and smoke checks.
