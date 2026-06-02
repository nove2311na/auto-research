# V1 Benchmark Contract

The original pack at `.docs/runbooks/new-claude-repo/` is the minimum benchmark for any repo produced by this seed system.

V2 starts from one idea, but the generated output must not be weaker than V1. V1 is the architecture and planning reference. V2 adds the idea-to-agent-system layer that makes the architecture generative.

## Minimum Parity With V1

Every generated repo must preserve V1's core architecture:

```text
Claude-facing layer       # CLAUDE.md, AGENTS.md, .claude/
Agentic knowledge layer   # agentic/knowledge, memory, policies, orchestration
Validation layer          # scripts/gates, hooks when needed, evals
Product code layer        # app/service/package/db/infra implementation
```

Every generated repo must include or explicitly justify:

- `CLAUDE.md`,
- `AGENTS.md`,
- `.claude/settings.json` or `.claude/settings.json.example`,
- `.claude/agents/`,
- `.claude/skills/`,
- `agentic/README.md`,
- `agentic/knowledge/`,
- `agentic/memory/`,
- `agentic/policies/`,
- `agentic/orchestration/`,
- `scripts/gates/`,
- a structure validation command,
- a quality gate command,
- a secret scan command,
- a no-silent-overwrite policy.

## Exceedance Required From V2

V2-generated repos must add these outputs beyond V1:

- `agentic/specs/agent-system-spec.md` or equivalent spec artifact,
- normalized `seed_input`,
- `agent_system_spec` with agents, skills, tools, MCP servers, workflows, memory, gates, scaffold files, and validation report,
- agent/skill/tool/MCP matrix,
- workflow contracts with retry limits and stop conditions,
- memory promotion rules,
- MCP risk and auth map,
- scaffold file plan with ownership and write mode,
- V1 benchmark alignment report.

## Target Scores

Generated repos should target:

| Gate | Minimum |
|---|---|
| V1 structure validator | Pass intended profile. |
| V1 quality rubric | `>= 3.8` production-ready baseline. |
| V2 seed rubric | `>= 4.0` ready for scaffold planning. |
| Hard gates | All pass. |

For a "perfect repo from one idea" target, aim for:

| Gate | Target |
|---|---|
| V1 structure validator | Pass full profile. |
| V1 quality rubric | `>= 4.3` excellent. |
| V2 seed rubric | `>= 4.5` excellent seed. |
| Agent/tool/MCP matrix | Complete, no broad unbounded access. |

## Idea-Only Input Rule

When the user gives only one rough idea, the seed system must still produce a complete provisional design.

Use conservative defaults:

- `target_runtime`: `claude_code`,
- `risk_level`: `standard`,
- `overwrite_policy`: `never`,
- `mcp_servers`: documented skips until auth and risk are known,
- `tools`: local read and deterministic gates first,
- `profile`: `standard` unless the idea implies regulated, external-write, production, auth, database, or infrastructure risk.

Ask follow-up questions only for safety-critical unknowns. Do not stop before producing a provisional `agent_system_spec`.

## Alignment Report

The final `validation_report` must include:

```json
{
  "v1_benchmark_alignment": {
    "structure_profile": "standard",
    "expected_v1_validator": "pass",
    "v1_quality_target": 4.3,
    "v2_seed_quality_target": 4.5,
    "parity_items": ["CLAUDE.md", ".claude/agents", "agentic/policies", "scripts/gates"],
    "exceedance_items": ["agent_system_spec", "tool_mcp_matrix", "workflow_contracts"],
    "documented_skips": []
  }
}
```

If any V1 parity item is skipped, the report must state why the generated repo can still meet the user goal.

