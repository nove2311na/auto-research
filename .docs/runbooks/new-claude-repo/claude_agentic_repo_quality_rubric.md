# Claude Agentic Repo Quality Rubric

Pack: `new-claude-repo`

Rubric này dùng để chấm chất lượng một repo Claude Code-native agentic sau khi scaffold hoặc retrofit. Nó bổ sung cho blueprint bằng hai lớp:

- **Rubric-based review**: chấm điểm chất lượng từng folder/file và tổng thể.
- **Rule-based structure gate**: kiểm tra cấu trúc tối thiểu có giống contract đã đề ra không.

## 1. Scale

Dùng thang 1-5:

| Score | Meaning | Descriptor |
|---|---|---|
| 1 | Missing / harmful | Thiếu hẳn hoặc có nội dung dễ gây lỗi/nguy hiểm. |
| 2 | Weak | Có file/folder nhưng sơ sài, không đủ hướng dẫn hoặc không dùng được. |
| 3 | Adequate | Đủ baseline, agent có thể dùng nhưng còn thiếu polish/coverage. |
| 4 | Strong | Rõ ràng, có guardrails, có validation, ít ambiguity. |
| 5 | Excellent | Reusable, calibrated, có deterministic checks, dễ mở rộng và ít context waste. |

Recommended thresholds:

```text
>= 4.3  Excellent
>= 3.8  Production-ready baseline
>= 3.2  Usable but needs hardening
<  3.2  Needs revision before relying on agents
```

Hard gates:

```text
[ ] No committed secrets
[ ] No silent overwrite policy
[ ] No destructive commands allowed by default
[ ] CLAUDE.md exists
[ ] .claude/settings.json exists
[ ] Validation commands are documented
```

If a hard gate fails, the repo cannot be marked production-ready regardless of average score.

## 2. Overall Rubric

| Criterion | Weight | 1 | 3 | 5 |
|---|---:|---|---|---|
| Claude-facing clarity | 12% | Claude entrypoint missing/confusing | `CLAUDE.md` exists with basic commands/rules | Concise briefing, clear workflows, links to deeper docs |
| Agent role design | 12% | Agents absent or overlapping | Core agents exist with basic roles | Roles are bounded, tools limited, output contracts clear |
| Skill workflow quality | 10% | Skills absent or verbose docs only | Core skills exist and are usable | Skills are concise, triggerable, progressive disclosure applied |
| Safety and permissions | 12% | Secrets/destructive commands not controlled | Basic deny/ask rules exist | Settings + hooks + policies enforce high-risk behavior |
| Validation and gates | 12% | No deterministic validation | Basic quality/secret gate exists | Stack-aware gates, structure checker, evals, clear acceptance |
| Knowledge and memory | 10% | Knowledge mixed into prompts/transcripts | `agentic/knowledge` and memory candidates exist | Durable/candidate split, promotion rules, auto-update loop |
| Move-safe layout | 8% | Path logic scattered, commands break after move | Some wrappers/path conventions exist | Stable public surface, `src` implementation, central path resolver |
| Harness loop integrity | 10% | No harness separation; model self-executes | Basic tool boundary exists | Full harness loop: validate → authorize → execute → observe |
| Loop budgets & stopping | 8% | No budget/stopping conditions | Some max_retries defined | Budget dimensions set, measurable stop conditions, compaction preserves state |
| Generator safety | 6% | Scaffold overwrites files | Basic no-overwrite policy | Conflict report, dry-run, merge policy, move log |

Score formula:

```text
weighted_score = sum(score * weight)
```

Use both:

- **weighted score** for overall quality,
- **hard gates** for pass/fail readiness.

## 3. Folder-Level Rubric

### 3.1. Root

Expected:

```text
CLAUDE.md
.gitignore
.mcp.json or documented skip
```

Score 5 when:

- `CLAUDE.md` is concise and project-specific.
- `.gitignore` blocks local/private files.
- `.mcp.json` has no secrets or is intentionally skipped.
- Root does not become a junk drawer.

Common failures:

- `CLAUDE.md` imports huge docs by default.
- `.env` or local settings are not gitignored.
- Commands are generic and do not match the repo.

### 3.2. `.claude/`

Expected:

```text
.claude/settings.json
.claude/rules/
.claude/agents/
.claude/skills/
.claude/hooks/        # required for full profile, optional otherwise
```

Score 5 when:

- settings deny secrets and dangerous shell.
- rules are path-scoped when appropriate.
- agents have distinct responsibilities and limited tools.
- skills are procedural, not bloated documentation.
- hooks fail safe and do not leak secrets.

Common failures:

- all agents can edit everything,
- reviewer/security agents mutate files by default,
- hooks log sensitive payloads,
- settings allow destructive commands silently.

### 3.3. `agentic/`

Expected:

```text
agentic/knowledge/
agentic/memory/
agentic/orchestration/
agentic/policies/
agentic/evals/        # standard/full
agentic/logs/         # full
```

Score 5 when:

- knowledge is stable and discoverable,
- memory candidates are separated from durable memory,
- policies name approval gates and risk levels,
- orchestration docs define handoff contracts,
- evals support regression and red-team cases.

Common failures:

- dumping raw transcripts into durable memory,
- no source/validation field for memory,
- policies are vague and not actionable.

### 3.4. `scripts/gates/`

Expected:

```text
run-quality-gate.*
scan-secrets.*
validate_agentic_structure.py
validate-migration.*       # if db/ exists or full profile
validate-memory-card.*     # if memory system exists
```

Score 5 when:

- gates are deterministic,
- scripts are stack-aware,
- failures explain next action,
- generated output can be checked by CI or local command.

Common failures:

- “run tests” documented but no command,
- secret scan ignores repo,
- gate always passes.

### 3.5. `src/<package>/`

Expected when repo has implementation code:

```text
src/<package>/paths.py
src/<package>/cli/
src/<package>/tools/
```

Score 5 when:

- code imports package paths,
- root scripts are wrappers,
- runtime anchors remain stable,
- layout can be moved without breaking public commands.

Common failures:

- scattered `parents[1]` path logic,
- imports depend on current working directory,
- scripts contain large implementation logic.

## 4. File-Level Rubric

### 4.1. `CLAUDE.md`

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Specificity | Generic boilerplate | Some repo-specific commands | Accurate repo map, commands, risk areas |
| Brevity | Too long/noisy | Manageable but includes details | Concise entrypoint with links |
| Workflow | No process | Basic plan/implement/test | Clear explore-plan-implement-validate-review |
| Safety | No hard rules | Mentions secrets/destructive risk | Names approval gates and high-risk domains |

### 4.2. `.claude/settings.json`

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Secret protection | Missing | Denies obvious `.env` | Denies secrets/credentials patterns and sensitive paths |
| Command safety | Destructive allowed | Some ask/deny | Allow/ask/deny aligned to risk |
| Hook wiring | Broken/missing | Basic hook references | Hooks exist, fail safe, documented |
| Merge safety | Overwrites user config | Manual edits only | Structural merge policy for generator |

### 4.3. `.claude/agents/*.md`

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Trigger description | Vague | Usable | Specific “when to use” trigger |
| Tool boundary | Too broad | Mostly reasonable | Minimal tools for role |
| Output contract | Freeform | Basic summary | Structured verdict/plan/evidence contract |
| Stop conditions | None | Some warnings | Clear stop/escalation rules |

### 4.4. `.claude/skills/*/SKILL.md`

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Frontmatter | Missing/invalid | name + description | Description includes clear triggers |
| Procedure | Vague advice | Step workflow | Reusable, concise, decision-complete workflow |
| Resources | Missing or cluttered | Some refs/scripts | Progressive disclosure, only useful resources |
| Validation | None | Suggested checks | Deterministic scripts or acceptance output |

### 4.5. Hooks

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Safety | Can leak/block wrong thing | Blocks basic risks | Blocks high-risk actions and redacts sensitive input |
| Robustness | Crashes on missing fields | Handles common cases | Fail-safe, cross-platform note, clear decisions |
| Observability | No logging | Basic logs | Useful logs without secrets |

### 4.6. Memory Files

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Candidate split | Raw memory mixed | Candidate file exists | Candidate/durable lifecycle is explicit |
| Source evidence | None | Some notes | Source, validation, confidence required |
| Reusability | Transcript dumps | Summaries | Concise reusable cards |

## 5. Self-Review Report Format

After scaffold, agent should produce:

```yaml
overall:
  weighted_score:
  readiness: block | needs_revision | usable | production_ready
  hard_gates_failed:
folder_scores:
  root:
  claude:
  agentic:
  scripts_gates:
  src_layout:
file_scores:
  CLAUDE.md:
  .claude/settings.json:
  agents:
  skills:
  hooks:
  memory:
required_fixes:
optional_improvements:
validation_commands:
evidence:
```

## 6. Calibration Examples

### Minimal repo that should score around 3.2

- Has `CLAUDE.md`, `.claude/settings.json`, one global rule, quality gate.
- No subagent team.
- No memory/policy system.
- No loop budgets or harness separation.
- Good for small repo, not enough for high-risk work.

### Standard repo that should score around 4.0

- Has core agents, skills, policies, memory candidates, quality gate.
- Hooks may be partial.
- Has basic loop budgets in `pipeline.json` or agent frontmatter.
- Memory has candidate/durable split.
- Good for day-to-day agentic development.

### Full governed repo that should score 4.5+

- Has hooks, evals, policy, memory promotion, security gates, ADR workflow.
- Has rule-based structure validator.
- Harness loop fully separated from model; all tool calls get results.
- Loop budgets across all dimensions (retries, time, tokens, cost).
- Measurable stop conditions per agent.
- Memory auto-update loop in agent instructions.
- Skills use progressive disclosure; stage-to-skill mapping documented.
- Good for repeated multi-agent work and repo generation.

---

## 7. Extended File-Level Rubric

### 7.1. Harness Loop Integrity

Applies to: `.claude/agents/*.md`, `agentic/policies/`, hooks

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Model/harness separation | Model self-executes actions | Some tool boundary exists | Model only proposes; harness validates+executes |
| Every tool gets a result | Missing results on error/denial | Timeout handled | Denial, timeout, error, abort all return observations |
| Draft/commit separation | External writes happen immediately | Some approval for high-risk | All external/financial/destructive require approval record |
| Tool schema narrowness | Broad tools like `execute_anything` | Mostly scoped | All tools narrow, typed, locally validated |

### 7.2. Loop Budgets và Stopping Conditions

Applies to: `pipeline.json`, `agentic/policies/loop-budgets.md`, agent frontmatter

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Budget defined | No budgets | Only max_retries | All dimensions: retries, tool calls, time, tokens, cost |
| Stopping condition | Vague "when done" | Some explicit checks | Measurable done condition (artifact exists AND validator pass) |
| Compaction safety | Compaction erases active state | Some state preserved | Plan, approvals, rules, artifacts all preserved across compaction |
| Escalation path | Agent loops indefinitely | Retries then stops | Clear escalate/abort conditions on budget exhaustion |

### 7.3. Memory Auto-Update Loop

Applies to: `agentic/memory/`, `CLAUDE.md` agent instructions

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Auto-update instruction | No instruction to update memory | Manual update mentioned | Explicit "update memory after correction" in agent instructions |
| Candidate/durable split | Raw memory dumped into one file | Candidates folder exists | Full lifecycle: candidate → validate → promote → archive |
| Size hygiene | Files grow unbounded | Some pruning noted | Files capped, archive path defined, anti-duplication rule |
| Preferences captured | No personalized memory | Working preferences noted | `preferences.md` maintained per team/user, prevents repeated mistakes |

### 7.4. Parallel Workers / Dynamic Workflow

Applies to: `pipeline.json`, `agentic/orchestration/`, agent specs

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Mode selection rationale | Always parallel or always sequential | Mode mentioned | Explicit decision rule: when to use sequential vs parallel vs fan-out |
| Worker isolation | Workers share output paths | Separate output folders | Strict path isolation + no cross-reading between workers |
| Critic integration | Workers self-validate | Critic invoked after parallel | Only critic picks winner; workers never self-validate |
| Budget enforcement | No total budget across workers | Per-worker budgets | Total aggregate budget across all parallel workers |

