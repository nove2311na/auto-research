# Scaffold Output Contract

V2 uses two contracts:

- `seed_input`: what the user or intake agent provides.
- `agent_system_spec`: what the seed system must produce before scaffolding.

## `seed_input`

Required fields:

| Field | Type | Requirement |
|---|---|---|
| `idea` | string | Concise statement of the repo purpose. |
| `jobs_to_be_done` | string array | Concrete jobs the future agentic repo must perform. |
| `domain` | string | Domain or operating context. |
| `target_runtime` | string | `claude_code`, `claude_code_plus_hcom`, or `generic_agentic`. |
| `stack` | string array | Languages, package managers, OS constraints, and runtime tools. |
| `risk_level` | string | `low`, `standard`, `high`, or `regulated`. |
| `reference_repos` | string array | Repos or docs to harvest before design. |
| `required_tools` | string array | Local tools, APIs, or MCP capabilities needed. |
| `constraints` | string array | Safety, path, auth, budget, or style limits. |
| `success_criteria` | string array | Measurable acceptance criteria. |

## `agent_system_spec`

Required top-level fields:

| Field | Type | Requirement |
|---|---|---|
| `summary` | object | One-paragraph system overview plus assumptions. |
| `agents` | array | Agent contracts. |
| `skills` | array | Skill contracts. |
| `tools` | array | Tool contracts. |
| `mcp_servers` | array | MCP contracts or documented skips. |
| `workflows` | array | Workflow contracts with triggers and gates. |
| `memory` | array | Knowledge, memory, candidate, and log contracts. |
| `gates` | array | Deterministic validation gates. |
| `scaffold_files` | array | File plan with source template and overwrite policy. |
| `validation_report` | object | Rubric score, hard gates, V1 benchmark alignment, and unresolved assumptions. |

## File Plan Contract

Every `scaffold_files[]` item must include:

| Field | Requirement |
|---|---|
| `path` | Repo-relative target path. |
| `kind` | `file` or `directory`. |
| `owner` | Human, seed agent, generator, or specific agent. |
| `source_template` | Template path or generated content contract. |
| `write_mode` | `create_only`, `merge_with_report`, or `manual`. |
| `validation` | Command or rule that checks the file. |

Default `write_mode` is `create_only`.

## Minimal Scaffold Surface

The generated repo should include at least:

```text
CLAUDE.md
AGENTS.md
.claude/settings.json.example
.claude/agents/
.claude/skills/
.mcp.json.example
agentic/README.md
agentic/knowledge/
agentic/memory/
agentic/policies/
agentic/orchestration/
agentic/specs/agent-system-spec.md
scripts/gates/
```

The exact files depend on the seed, but every omitted area must be explained in `validation_report.documented_skips`.

## V1 Benchmark Alignment

Every `agent_system_spec.validation_report` must include `v1_benchmark_alignment`.

Required fields:

| Field | Requirement |
|---|---|
| `structure_profile` | Intended V1 profile: `minimal`, `standard`, or `full`. |
| `expected_v1_validator` | Expected V1 validator result. |
| `v1_quality_target` | Numeric target from the V1 rubric. |
| `v2_seed_quality_target` | Numeric target from the V2 rubric. |
| `parity_items` | V1 features included in the scaffold plan. |
| `exceedance_items` | V2 additions beyond V1. |
| `documented_skips` | Skipped V1 items and reasons. |
