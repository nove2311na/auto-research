---
name: reference-harvest
description: Collect and distill official docs, skill repos, agent repos, and MCP references before designing specialized Claude Code scaffold content. Use before writing custom agents, skills, tools, or workflows.
---

# Reference Harvest

## Use When

- A seed names external docs or repos.
- A new specialized skill, agent, workflow, or MCP map is being designed.
- The design needs source-grounded patterns.

## Workflow

1. Read the requested source list.
2. Prefer official docs and primary repositories.
3. Run list or inspect commands that do not install or vendor files when available.
4. Distill the source into takeaways that affect design.
5. Record command results and blocked checks.
6. Hand the source index back to the system architect.

## Required Output

- source title,
- URL or local path,
- date checked,
- distilled takeaway,
- design consequence,
- command evidence when available.

## Validation

The source index must include takeaways, not only links.

## Pack Layout

- `references/` stores source notes.
- `scripts/` stores source-inspection helpers.
- `assets/` stores diagrams or screenshots when useful.

