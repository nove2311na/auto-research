# V2 Comparison Note

V1 and V2 serve different parts of the same scaffold workflow.

## V1 Focus

`.docs/runbooks/new-claude-repo/` defines a Claude-native repo structure:

- stable public surface,
- four-layer repo model,
- folder and file contracts,
- move-safe layout guidance,
- structure validator for generated repos,
- quality rubric for scaffolded repos.

V1 answers: "Does this repo look like a Claude Code-native agentic repo?"

## V2 Focus

`.docs/runbooks/new-claude-repo-seed-v2/` starts earlier:

- idea intake,
- reference harvest,
- jobs-to-be-done decomposition,
- agent, skill, tool, and MCP matrix,
- workflow and memory design,
- scaffold output contract,
- seed-specific quality rubric,
- pack validator.

V2 answers: "Given this rough idea, what agentic system should be scaffolded?"

V2 must not weaken V1. For generation work, V1 is the minimum output benchmark and V2 is the planning intelligence that makes the benchmark reachable from one idea.

## What V2 Adds

- A normalized `seed_input` contract for vague user ideas.
- An `agent_system_spec` output contract before file generation.
- Required agent specs with allowed tools, forbidden actions, outputs, stop conditions, and escalation.
- Required skill specs following `SKILL.md` plus `references/`, `scripts/`, and `assets/`.
- Required tool and MCP specs with risk class, auth, approval policy, and allowed agents.
- A reference repo index that records distilled takeaways instead of vendoring repos.
- A seed rubric that scores idea-to-system quality, not only folder structure.
- Minimal generated-repo templates for Claude entrypoints, subagents, skills, MCP config, knowledge, memory, and policies.
- A V1 benchmark contract that requires generated repos to match or exceed the original architecture and rubric.

## Recommended Combined Flow

1. Use V2 to turn the idea into `agent_system_spec`.
2. Use V2 templates for the first scaffold plan.
3. Use V1 blueprint and validator to check the generated repo structure.
4. Use V1 rubric for the repo and V2 rubric for the seed quality.
5. Iterate until the repo passes V1 parity and V2 exceedance checks.
