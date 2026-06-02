# New Claude Repo Seed V2

This pack turns a rough project idea into a Claude Code-native agentic repo specification.

It is intentionally isolated from `.docs/runbooks/new-claude-repo/`. V1 is a structural blueprint and readiness gate. V2 is an idea germination system: it starts from jobs-to-be-done and produces a complete `agent_system_spec` before any repo scaffold is written.

## Use Case

Use this pack when the input sounds like:

```text
I want an agentic repo that can do work A, work B, and work C.
```

The output should answer:

- which agents are needed,
- which skills are reusable procedures,
- which tools and MCP servers are allowed,
- which workflows run in sequence or parallel,
- which memory and knowledge files are durable,
- which gates prove the scaffold is usable,
- which files should be created without overwriting existing work.

## Pack Files

| File | Purpose |
|---|---|
| `seed_prompt.md` | Static prompt for converting an idea into a full agentic system spec. |
| `growth_protocol.md` | Stage-by-stage germination flow from intake to validation report. |
| `v1_benchmark_contract.md` | Mandatory parity-and-exceedance contract against `.docs/runbooks/new-claude-repo/`. |
| `agent_skill_tool_matrix.md` | Required contracts for agents, skills, tools, and MCP servers. |
| `mcp_catalog.md` | Risk classes, approval policies, and MCP selection rules. |
| `reference_repo_index.md` | Curated source index and distilled takeaways. |
| `scaffold_output_contract.md` | Input and output schemas for `seed_input` and `agent_system_spec`. |
| `quality_rubric.md` | Rubric for scoring idea-to-agentic-system quality. |
| `comparison_note.md` | What V2 adds over the original V1 pack. |
| `schemas/` | Machine-readable JSON schemas for the seed input and system spec. |
| `templates/` | Minimal generated-repo template pack. |
| `scripts/validate_seed_pack.py` | Deterministic pack validator. |

## Workflow

1. Fill the `seed_input` contract in `scaffold_output_contract.md`.
2. Run the stages in `growth_protocol.md`.
3. Produce an `agent_system_spec` that satisfies the output contract.
4. Check `v1_benchmark_contract.md`; V1 quality is the minimum output bar, not optional inspiration.
5. Map every agent, skill, tool, MCP server, workflow, memory file, and gate through `agent_skill_tool_matrix.md`.
6. Use `templates/` as the minimum scaffold surface.
7. Run the validator:

```cmd
python .docs\runbooks\new-claude-repo-seed-v2\scripts\validate_seed_pack.py --target .docs\runbooks\new-claude-repo-seed-v2
```

## Non-Goals

- This is not a full CLI generator.
- This does not vendor external repositories.
- This does not change `.docs/runbooks/new-claude-repo/`.
- This does not make MCP installation decisions without auth and risk review.

## Quality Bar

The seed system must be able to produce a repo that is at least as complete as the architecture in `.docs/runbooks/new-claude-repo/`.

Minimum generated output:

- satisfies V1's stable public surface,
- includes V1's four-layer repo model,
- passes V1-style structure validation at the intended profile,
- scores at least production-ready baseline on the V1 rubric,
- adds V2's idea-to-system contracts, agent/skill/tool/MCP matrix, workflow design, memory design, scaffold file plan, and seed validation report.
