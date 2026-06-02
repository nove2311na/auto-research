# Reference Repo Index

Checked on 2026-06-02. This pack records source links and distilled takeaways only. It does not vendor external repositories.

## Official and Primary Sources

| Source | Link | Distilled Takeaway |
|---|---|---|
| Claude Code settings | https://code.claude.com/docs/ja/settings | Settings are part of the permission and hook surface, so a generated repo must separate soft instructions from enforceable configuration. |
| Claude Code subagents | https://code.claude.com/docs/id/sub-agents | Subagents need bounded roles, activation descriptions, and tool access. V2 mirrors that with required agent contracts. |
| Claude Code MCP and SDK | https://code.claude.com/docs/en/agent-sdk/mcp | MCP servers must be mapped to risk, auth, and allowed agents before being added to a scaffold. |
| Agent Skills specification | https://agentskills.io/specification | A skill should be triggerable, procedural, and organized for progressive disclosure through `SKILL.md`, `references/`, `scripts/`, and `assets/`. |
| Anthropic skills | https://github.com/anthropics/skills | Skills are reusable procedures with narrow triggers and supporting resources, not generic documentation dumps. |

## Repo Pattern Sources

| Repo | Link | Distilled Takeaway |
|---|---|---|
| ShakaCode shared commands, agents, and skills | https://github.com/shakacode/claude-code-commands-skills-agents | Shared commands and skills should remain project-legible, with docs standards and clear trigger behavior. |
| Claude Memory Kit | https://github.com/awrshift/claude-memory-kit | Memory needs layers: daily or session records, hot cache, role references, and canonical rules. Promotion should be explicit. |
| Claude Agent Starter | https://github.com/enc0ding/claude-agent-starter | Repo-starting tools should classify what kind of artifact is being installed before copying files. |
| Claude Agents | https://github.com/iannuttall/claude-agents | Agent collections are useful only when roles and invocation rules are clear enough to avoid overlap. |
| OneWave Claude Skills | https://github.com/OneWave-AI/claude-skills | Large catalogs show why skill discovery needs trigger descriptions, taxonomy, and risk-aware selection. |

## Local Reference-Learning Commands

These commands were run with list mode to fetch and inspect available skill patterns without installing or vendoring them into this workspace:

```cmd
npx -y skills add anthropics/skills --list --full-depth
npx -y skills add shakacode/claude-code-commands-skills-agents --list --full-depth
npx -y skills add awrshift/claude-memory-kit --list --full-depth
npx -y skills add enc0ding/claude-agent-starter --list --full-depth
npx -y skills add OneWave-AI/claude-skills --list --full-depth
```

Observed results:

| Repo | Result |
|---|---|
| `anthropics/skills` | 18 skills found, including `skill-creator`, `mcp-builder`, and document skills. |
| `shakacode/claude-code-commands-skills-agents` | 1 docs skill found. |
| `awrshift/claude-memory-kit` | 3 skills found, including `claude-memory-kit`, `close-day`, and `tour`. |
| `enc0ding/claude-agent-starter` | 1 installer classification skill found. |
| `OneWave-AI/claude-skills` | 154 skills found, including team, swarm, workflow, and skill navigation patterns. |

## Design Consequences for V2

- Reference learning is a required stage before specialized scaffold design.
- The seed output must include source takeaways, not only links.
- Broad skill catalogs are inputs for role and trigger taxonomy, not direct templates to copy.
- Memory and MCP are optional capabilities, but their contracts must exist when the seed asks for them.

