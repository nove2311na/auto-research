# MCP Catalog and Risk Policy

MCP servers extend agent capability. Treat them as part of the security model, not as decoration.

## Risk Classes

Use the field name `risk_class` in every tool and MCP server spec.

| Class | Meaning | Default Policy |
|---|---|---|
| `R0` | Local read-only inspection. | allow |
| `R1` | Local write inside approved workspace. | ask |
| `R2` | External read or web/API fetch. | ask |
| `R3` | External write, messaging, ticketing, cloud mutation. | ask with explicit purpose |
| `R4` | Destructive, admin, secrets, billing, production data. | deny unless human approves per task |

## Approval Rules

- `R0` can be allowed to research and gatekeeper agents.
- `R1` requires a target path and no-overwrite policy.
- `R2` requires source citation or retrieval log.
- `R3` requires named destination, payload summary, and rollback option when possible.
- `R4` requires human approval and a validation plan.

## Candidate MCP Servers

| MCP Server | Purpose | Risk | Auth | Allowed Agents | Notes |
|---|---|---:|---|---|---|
| filesystem | Read or write approved project files. | R0/R1 | none | idea-harvester, scaffold-planner, gatekeeper | Configure path scope tightly. |
| git | Inspect status, diffs, branches, and history. | R0/R1 | local git identity | gatekeeper, scaffold-planner | Commits require explicit human request. |
| web-fetch | Fetch official docs and source pages. | R2 | none or provider token | reference-harvester | Prefer official docs and primary repos. |
| database | Inspect schemas or run migrations. | R2/R4 | database credentials | gatekeeper only by default | Writes require migration gate. |
| issue-tracker | Read or write project tasks. | R2/R3 | OAuth or API token | workflow-designer, gatekeeper | External writes require approval. |
| memory | Store curated project memory. | R1/R3 | local or service auth | gatekeeper, memory-curator | Promotion requires source and validation status. |
| messaging | Send notifications or handoffs. | R3 | bot token or OAuth | gatekeeper only by default | Never send secrets or raw private logs. |

## `.mcp.json` Guidance

Project-level `.mcp.json` should include only servers that are safe to share with the repo. Secrets must live in user-level config or an approved secret manager.

If no MCP servers are required, generate `.mcp.json.example` and document the skip in `agentic/policies/approval-gates.md`.
