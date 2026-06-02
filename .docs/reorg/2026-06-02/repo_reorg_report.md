# Repo Reorg Report

Status: validated

## Changes

- Added user-facing runbook: `.docs/runbooks/pipeline_start_guide.md`.
- Added docs index: `.docs/README.md`.
- Moved loose audit/report docs into `.docs/reports/`.
- Moved the Claude Scholar proposal into `.docs/plans/`.
- Updated root `README.md` quick-start commands and file map.
- Added `agents/<role>/AGENT.md` compatibility shims so legacy references do not point to missing paths.
- Added `src/research_pipeline/` as the canonical Python implementation package.
- Moved core implementation modules into `src/research_pipeline/tools/`, `src/research_pipeline/gates/`, and `src/research_pipeline/cli/`.
- Kept root `scripts/`, `tools/`, and `gates/` as compatibility wrappers so old commands/imports keep working.
- Added `src/research_pipeline/paths.py` as the central path resolver for repo/runtime paths.

## Runtime Paths Preserved

- `scripts/` (wrapper entrypoints)
- `tools/` (compatibility shims)
- `schemas/`
- `.claude/`
- `.docs/agentic/`
- `gates/` (compatibility shims + docs)
- `evals/`
- `observability/`
- `outputs/`

## Validation

- `python -m py_compile ...` passed.
- `python scripts\validate_specs.py` passed with `ALL VALIDATIONS PASSED`.
- `python scripts\smoke_v2.py` passed with `ALL V2 SMOKE CHECKS PASSED`.

## Follow-up Notes

- `evals/` and `observability/` intentionally remain at root because they are runtime/governance data folders, not importable package code.
- Root `tools/` and `gates/` intentionally remain as shims for agent prompts and old imports.
- `.docs/agentic/` intentionally remains at its current path because `.claude/agents/*`, `.claude/skills/*`, hooks, and schema descriptions reference it.
- The cleanup did not move runtime files or outputs.
