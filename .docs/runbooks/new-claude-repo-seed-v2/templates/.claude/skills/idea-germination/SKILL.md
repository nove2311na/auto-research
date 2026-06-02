---
name: idea-germination
description: Turn a rough project idea into a complete agent_system_spec for a Claude Code-native agentic repo. Use when the user describes jobs they want an agentic repo to perform and needs agents, skills, tools, MCP servers, workflows, memory, gates, and scaffold files designed.
---

# Idea Germination

## Use When

- The user gives a rough idea instead of a full spec.
- The repo needs an agent team design before scaffolding.
- The output should be a validated `agent_system_spec`.

## Workflow

1. Normalize the idea into `seed_input`.
2. Read `references/README.md` for source categories.
3. Ask the reference harvester to collect source takeaways when external patterns are needed.
4. Decompose jobs-to-be-done into agents, skills, tools, workflows, memory, and gates.
5. Write the `agent_system_spec`.
6. Score the result with the seed rubric.
7. Produce a scaffold plan with create-only write mode.

## Required Output

- normalized `seed_input`,
- `agent_system_spec`,
- scaffold plan,
- validation report.

## Validation

Run the seed pack validator and rubric check before claiming completion.

## Pack Layout

- `references/` stores source notes and distilled patterns.
- `scripts/` stores helper checks.
- `assets/` stores reusable diagrams or static artifacts.

