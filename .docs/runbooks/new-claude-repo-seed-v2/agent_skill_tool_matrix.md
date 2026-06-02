# Agent, Skill, Tool, and MCP Matrix

The matrix prevents vague agent teams. Every role and capability must have an owner, contract, risk class, and validation path.

## Agent Spec Contract

Each `agents[]` item must include:

| Field | Requirement |
|---|---|
| `name` | Stable lowercase identifier. |
| `role` | One bounded responsibility. |
| `trigger` | When this agent should be invoked. |
| `allowed_tools` | Explicit tool list. |
| `forbidden_actions` | Actions the agent must not take. |
| `input_contract` | Required input fields. |
| `output_contract` | Required output fields and artifact paths. |
| `stop_conditions` | Objective conditions that end the agent run. |
| `escalation` | When to hand back to human or lead agent. |

## Seed Agent Roles

| Agent | Role | Trigger | Allowed Tools | Forbidden Actions | Output |
|---|---|---|---|---|---|
| `idea-harvester` | Normalize rough project intent into `seed_input`. | New idea, vague scope, missing jobs-to-be-done. | Read, search, local file inspection. | Writing scaffold files, approving external writes. | Normalized seed and assumptions. |
| `reference-harvester` | Gather source patterns and distilled takeaways. | Seed names repos, docs, or specialized workflows. | Web/search when allowed, `npx skills add --list`, local source index. | Vendoring repos, installing skills without approval. | Reference harvest report. |
| `system-architect` | Convert jobs into agent, skill, tool, memory, and gate design. | Seed input is complete enough to design. | Read, write spec drafts. | Running external side effects. | `agent_system_spec`. |
| `workflow-designer` | Define workflows, handoffs, retries, and stop conditions. | Multiple jobs or agents need coordination. | Read, write workflow docs. | Broad tool grants without risk mapping. | Workflow contracts. |
| `scaffold-planner` | Produce file plan and template mapping. | System spec is approved or ready for generation. | Read, write scaffold plan. | Overwriting files silently. | Scaffold file manifest. |
| `gatekeeper` | Score, validate, and check V1 benchmark alignment. | Any spec or scaffold plan is complete. | Read, run validators and gates. | Editing producer artifacts during review. | Validation report, V1 alignment, and rubric score. |

## Skill Spec Contract

Each `skills[]` item must include:

| Field | Requirement |
|---|---|
| `name` | Directory name under `.claude/skills/<name>/`. |
| `description` | Trigger-oriented description, not marketing copy. |
| `when_to_use` | Clear activation conditions. |
| `workflow` | Ordered procedural steps. |
| `references` | Files under `references/` loaded only when needed. |
| `scripts` | Optional helper scripts under `scripts/`. |
| `assets` | Optional reusable assets under `assets/`. |
| `validation` | How the skill proves completion. |

Minimum seed skills:

- `idea-germination`: convert idea seed into normalized input and system spec.
- `reference-harvest`: collect and distill repo/doc patterns without vendoring.
- `quality-gate`: score the produced spec and scaffold plan.

## Tool Spec Contract

Each `tools[]` item must include:

| Field | Requirement |
|---|---|
| `name` | Stable tool name. |
| `purpose` | Narrow reason the tool is needed. |
| `risk_class` | One of `R0` through `R4`. |
| `approval_policy` | `allow`, `ask`, or `deny` by default. |
| `auth_requirements` | Required credentials or `none`. |
| `allowed_agents` | Agent names that may use the tool. |
| `validation` | How usage is logged or checked. |

## MCP Spec Contract

Each `mcp_servers[]` item must include:

| Field | Requirement |
|---|---|
| `name` | Project-local MCP identifier. |
| `package_or_command` | Command or package reference. |
| `purpose` | Specific capability. |
| `risk_class` | Data and side-effect risk. |
| `approval_policy` | Default permission stance. |
| `auth_requirements` | Token, OAuth, local-only, or none. |
| `allowed_agents` | Agents allowed to call it. |
| `blocked_agents` | Agents that must not call it. |
| `config_path` | `.mcp.json`, user config, or documented skip. |
