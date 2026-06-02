# Notes

## Path Audit
- `gates/`, `evals/`, and `observability/` are referenced by Python modules and docs, so they stay at repo root.
- `.docs/agentic/` is referenced by `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `.claude/hooks/PreToolUse.py`, and schema descriptions, so it stays in place.
- `.docs/plan.md`, `.docs/Audit_Report.md`, and `.docs/dev_plans/*` are loose documentation with no runtime references found by `rg`; these are safe to group under `.docs/reports/` and `.docs/plans/`.
- Root `README.md` still describes the old `agents/<role>/AGENT.md` layout and old launch command; update it to match current `.claude/agents` and Python scripts.

## Safety Decision
This cleanup is documentation-focused. Runtime code layout is intentionally preserved to avoid path regressions.

## Compatibility Shims
- Added `agents/README.md` and `agents/<role>/AGENT.md` pointer files because legacy docs and agent spec JSON still describe `agents/<role>/`.
- Runtime behavior remains in `.claude/agents/*.md` and `.claude/agents/*.json`.
