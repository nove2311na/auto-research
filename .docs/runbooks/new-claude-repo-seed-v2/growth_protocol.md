# Growth Protocol

This protocol turns an idea seed into an agentic repo plan.

## Stage 0: Preflight

Goal: confirm scope and preserve existing work.

Inputs:

- target folder,
- overwrite policy,
- current file tree,
- current git status.

Actions:

- If target exists, stop or choose a timestamped suffix.
- Check whether `.claude/`, `CLAUDE.md`, `AGENTS.md`, `agentic/`, and `scripts/gates/` already exist.
- Record detected stack, package manager, runtime, and high-risk folders.

Outputs:

- `preflight_report`,
- conflict list,
- safe scaffold target.

## Stage 1: Idea Intake

Goal: convert vague intent into a normalized seed.

Required fields:

- `idea`,
- `jobs_to_be_done`,
- `domain`,
- `target_runtime`,
- `stack`,
- `risk_level`,
- `reference_repos`,
- `required_tools`,
- `constraints`,
- `success_criteria`.

If a field is missing, infer conservatively from repo evidence. Ask only when the missing value changes safety or external access.

## Stage 2: Reference Harvest

Goal: learn from existing source material before inventing templates.

Minimum harvest:

- official Claude Code settings, subagents, and MCP docs,
- Agent Skills specification,
- Anthropic skills repository,
- one repo with shared commands, agents, and skills,
- one repo with memory design,
- one broad skill catalog for role and trigger patterns.

Do not vendor external repos. Record distilled takeaways and links in `reference_repo_index.md`.

## Stage 3: Job Decomposition

Goal: turn jobs-to-be-done into system responsibilities.

For each job, identify:

- primary agent,
- supporting agents,
- reusable skill,
- required tools,
- required MCP servers,
- durable knowledge,
- memory candidates,
- gates,
- success signal,
- failure loop.

## Stage 4: Agent, Skill, Tool, MCP Matrix

Goal: make access and responsibility explicit.

Use `agent_skill_tool_matrix.md` to produce:

- `agents[]`,
- `skills[]`,
- `tools[]`,
- `mcp_servers[]`.

No agent should receive broad write or external-write access unless a workflow needs it and a gate covers it.

## Stage 5: Workflow Design

Goal: define how the system runs.

Every workflow requires:

- trigger,
- inputs,
- ordered steps,
- allowed parallel steps,
- output artifacts,
- retry limit,
- stop condition,
- escalation path,
- validation gate.

## Stage 6: Memory and Knowledge Design

Goal: prevent prompts from becoming long-lived storage.

Use this split:

- `agentic/knowledge/` for stable system facts,
- `agentic/memory/` for curated memory and memory candidates,
- `agentic/policies/` for risk and approval rules,
- `agentic/logs/` for local generated logs when enabled.

Memory promotion requires source, date, validation status, and owner.

## Stage 7: Scaffold Plan

Goal: produce a file plan before edits.

Every scaffold file requires:

- path,
- owner,
- source template,
- whether it is generated, copied, or merged,
- overwrite policy,
- validation command.

The default overwrite policy is `never`.

## Stage 8: Validation Report

Goal: prove the seed can generate an agentic system.

Run:

- structure validator,
- V1 benchmark alignment check,
- source index check,
- input contract check,
- output contract check,
- matrix completeness check,
- rubric score.

The seed is acceptable only when hard gates pass and the rubric score is at least 4.0.

## Stage 9: V1-Plus Readiness

Goal: ensure the generated repo is not weaker than `.docs/runbooks/new-claude-repo/`.

Checks:

- V1 four-layer architecture is present.
- V1 stable public surface is present.
- V1 deterministic gates are represented.
- V1 quality rubric target is named.
- V2 exceedance artifacts are present: `seed_input`, `agent_system_spec`, matrix, workflows, memory design, MCP risk map, scaffold file plan, validation report.

Output:

- `v1_benchmark_alignment`,
- parity gaps,
- exceedance evidence,
- revision loop if the generated repo falls below V1.
