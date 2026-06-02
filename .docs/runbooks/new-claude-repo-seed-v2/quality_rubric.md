# Seed Quality Rubric

This rubric scores how well V2 turns an idea into an agentic repo system.

## Scale

| Score | Meaning |
|---:|---|
| 1 | Missing or unsafe. |
| 2 | Present but vague, overlapping, or hard to validate. |
| 3 | Usable baseline with some gaps. |
| 4 | Strong, bounded, and verifiable. |
| 5 | Excellent, reusable, risk-aware, and easy to scaffold. |

Recommended thresholds:

```text
>= 4.5  Excellent seed
>= 4.0  Ready for scaffold planning
>= 3.5  Needs targeted revision
<  3.5  Redesign before scaffolding
```

## Hard Gates

The seed cannot pass when any hard gate fails:

- No silent overwrite policy.
- Every agent has role, trigger, allowed tools, forbidden actions, input, output, stop conditions, and escalation.
- Every external tool or MCP server has risk class, auth requirement, approval policy, and allowed agents.
- Every workflow has trigger, input, output, retry limit, stop condition, and validation gate.
- Source index exists and includes distilled takeaways.
- `agent_system_spec` satisfies the output contract.
- V1 benchmark alignment exists and targets at least V1 production-ready baseline.

## Weighted Rubric

| Criterion | Weight | Score 1 | Score 3 | Score 5 |
|---|---:|---|---|---|
| Idea fidelity | 12% | Spec ignores core jobs | Jobs mapped to basic roles | Every job has agent, workflow, gate, and success signal |
| Job decomposition | 10% | Work remains vague | Jobs split into major phases | Jobs become bounded responsibilities and artifacts |
| Reference grounding | 10% | No sources or copied material | Links recorded | Distilled takeaways shape decisions without vendoring |
| Agent boundaries | 12% | Agents overlap or all can do everything | Core roles exist | Boundaries, forbidden actions, and escalation are precise |
| Skill design | 10% | Skills are long docs | Skills have workflows | Skills are triggerable, procedural, and progressively disclosed |
| Tool and MCP safety | 12% | Tools granted broadly | Basic approvals exist | Risk, auth, allowed agents, and validation are explicit |
| Workflow quality | 10% | No handoffs or retries | Sequence is usable | Handoffs, parallelism, retries, and stop conditions are measurable |
| Memory design | 8% | Memory is prompt dumping | Knowledge and memory folders exist | Durable, candidate, and log layers have promotion rules |
| Scaffold completeness | 8% | File plan missing | Basic files named | Ownership, source templates, write modes, and validators are mapped |
| Validation strength | 8% | Only narrative review | Basic validator exists | Structure, schema, matrix, and rubric gates all run |

## V1 Benchmark Addendum

The weighted rubric is necessary but not sufficient. A V2 seed can score well only if the generated repo is designed to meet or exceed `.docs/runbooks/new-claude-repo/`.

Score 5 for V1 benchmark alignment when:

- V1 four-layer architecture is present,
- V1 stable public surface is present,
- V1 structure validator target is named,
- V1 quality rubric target is `>= 3.8`,
- seed output adds `agent_system_spec`, matrix, workflows, MCP risk map, memory promotion, and scaffold file plan.

Score 1 when V2 produces an interesting agent design that cannot generate a repo matching the V1 baseline.

## Self-Scoring Output

The `validation_report` should include:

```json
{
  "weighted_score": 4.2,
  "hard_gates": {
    "silent_overwrite_policy": "pass",
    "agent_contracts": "pass",
    "tool_mcp_contracts": "pass",
    "workflow_contracts": "pass",
    "source_index": "pass",
    "output_contract": "pass",
    "v1_benchmark_alignment": "pass"
  },
  "v1_benchmark_alignment": {
    "structure_profile": "standard",
    "v1_quality_target": 4.3,
    "v2_seed_quality_target": 4.5
  },
  "revision_notes": ["Tighten MCP auth assumptions before enabling external writes"]
}
```
