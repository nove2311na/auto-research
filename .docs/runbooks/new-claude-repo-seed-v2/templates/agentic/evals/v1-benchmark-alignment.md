# V1 Benchmark Alignment

Use this eval before accepting a generated repo.

## Parity Checks

- [ ] `CLAUDE.md` exists and is concise.
- [ ] `AGENTS.md` exists and records agent memory/invariants.
- [ ] `.claude/agents/` contains bounded roles.
- [ ] `.claude/skills/` contains procedural skills.
- [ ] `agentic/knowledge/` exists.
- [ ] `agentic/memory/` exists.
- [ ] `agentic/policies/` exists.
- [ ] `agentic/orchestration/` exists.
- [ ] `scripts/gates/` exists.
- [ ] Structure, quality, and secret scan gates are documented.
- [ ] No silent overwrite policy is documented.

## Exceedance Checks

- [ ] `agent_system_spec` exists.
- [ ] Agent/skill/tool/MCP matrix exists.
- [ ] Workflow contracts include retry limits and stop conditions.
- [ ] MCP risk and auth map exists.
- [ ] Memory promotion rule exists.
- [ ] Scaffold file plan includes owner, write mode, source template, and validation.

## Score Targets

- V1 structure validator: pass intended profile.
- V1 quality rubric: at least 3.8, target 4.3.
- V2 seed rubric: at least 4.0, target 4.5.

