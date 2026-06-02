# New Claude Repo Runbook Pack

This folder contains the complete reference pack for creating or retrofitting a Claude Code-native agentic repo.

## Files

- `claude_native_agentic_repo_blueprint.md` — canonical blueprint for folder contracts, build phases, generator workflow, and acceptance criteria. Includes sections on harness architecture, loop budgets, memory layer design, dynamic workflow/parallel workers, and skills progressive disclosure.
- `claude_agentic_repo_quality_rubric.md` — scoring rubric for overall, folder-level, and file-level review. Includes extended rubric for harness integrity, loop budgets, memory auto-update, and parallel workers.
- `movable_repo_layout_tips.md` — practical layout rules for keeping implementation movable without breaking public commands. Includes context engineering hierarchy and agent-legible environment design.
- `validate_agentic_structure.py` — deterministic structure checker for scaffolded repos.

## Suggested Reading Order

1. `claude_native_agentic_repo_blueprint.md` — start with Sections 1–5 (design principles), then 18–22 (harness, budgets, memory, parallel, skills)
2. `claude_agentic_repo_quality_rubric.md` — score after scaffolding; use Section 7 for extended criteria
3. `movable_repo_layout_tips.md` — consult before any layout refactor; read Sections 13–14 for context engineering
4. `validate_agentic_structure.py` — run after every scaffold or retrofit

## Validator Usage

From the repo root:

```cmd
python .docs\runbooks\new-claude-repo\validate_agentic_structure.py --target . --profile minimal
python .docs\runbooks\new-claude-repo\validate_agentic_structure.py --target . --profile standard
python .docs\runbooks\new-claude-repo\validate_agentic_structure.py --target . --profile full --json
```

When this pack is used to generate a new repo, copy the validator into the generated repo as:

```text
scripts/gates/validate_agentic_structure.py
```

## Sources

Local copies of cited source materials are in `sources/`:

| File | Mô tả |
|---|---|
| `sources/source-agentic-modes.md` | 3 Claude agent modes: Sub-Agent, Agent Team, Dynamic Workflow |
| `sources/source-build-a-agent.md` | Full transcript: context engineering, memory.md pattern, skills as SOPs |
| `sources/source-agents-best-practices-skill.md` | Harness loop, tool permissions, progressive disclosure, loop budgets, compaction safety |
| `sources/source-harnessed-llm-agent.png` | "A Harnessed LLM Agent" diagram (DailyDoseofDS.com) — harness component model |
| `sources/source-multi-agent-system.png` | "How to Build an AI Agent" infographic — 8-step framework + platform comparison |
| `sources/source-three-agent-modes.png` | "Ba Cách để Chạy Agents trong Claude Code" — Sub-Agent / Team / Dynamic Workflow |
| `sources/source-how-to-build-multi-agent.png` | Multi-Agent System infographic (n8nstack) — orchestrator + specialized agents |

