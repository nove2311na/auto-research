# New Claude Repo Runbook Pack

This folder contains the complete reference pack for creating or retrofitting a Claude Code-native agentic repo.

## Files

- `claude_native_agentic_repo_blueprint.md` — canonical blueprint for folder contracts, build phases, generator workflow, and acceptance criteria.
- `claude_agentic_repo_quality_rubric.md` — scoring rubric for overall, folder-level, and file-level review.
- `movable_repo_layout_tips.md` — practical layout rules for keeping implementation movable without breaking public commands.
- `validate_agentic_structure.py` — deterministic structure checker for scaffolded repos.

## Suggested Reading Order

1. `claude_native_agentic_repo_blueprint.md`
2. `claude_agentic_repo_quality_rubric.md`
3. `movable_repo_layout_tips.md`
4. `validate_agentic_structure.py`

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

