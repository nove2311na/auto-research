# Claude-Native Agentic Repo Blueprint

Pack: `new-claude-repo`

Tài liệu này đúc kết cấu trúc cần dựng khi muốn tạo một repo **native cho Claude Code** và tối ưu cho workflow **AI agentic**. Mục tiêu là đủ rõ để dùng làm input tạo:

- một skill scaffold repo agentic,
- một subagent chuyên dựng agentic folder,
- hoặc một agent/tool tự sinh `.claude/`, `agentic/`, hooks, gates, docs, memory, evals theo nhu cầu.

## 1. Mục tiêu thiết kế

Một repo agentic tốt không chỉ là codebase. Nó là workspace có 4 lớp:

```text
Claude-facing layer       # Claude Code đọc và dùng trực tiếp
Agentic knowledge layer   # knowledge, memory, policy, orchestration
Validation layer          # hooks, scripts, gates, evals
Product code layer        # app/service/package/db/infra thật
```

Tại sao cần 4 lớp:

- **Claude-facing layer** giúp Claude biết cách hành xử trong repo mà không phải hỏi lại mọi lần.
- **Agentic knowledge layer** giữ kiến thức dài hạn ngoài context chính để tránh `CLAUDE.md` phình to.
- **Validation layer** biến rule mềm thành check cứng bằng code/hook/script.
- **Product code layer** giữ code thật tách khỏi hệ thống điều phối agent.

Nguyên tắc quan trọng: `CLAUDE.md` và `.claude/rules/*` là **briefing/context**, không phải enforcement tuyệt đối. Những thứ cần chặn thật phải nằm ở `.claude/settings.json`, hooks, hoặc scripts/gates.

## 2. Design Principles

### 2.1. Stable contract, movable implementation

Repo nên có public surface ổn định:

```text
CLAUDE.md
.claude/
agentic/
scripts/gates/
src/<package>/
```

Các command, rule path, agent path, memory path nên ổn định. Code implementation có thể move, nhưng wrapper hoặc path resolver phải giữ contract.

Áp dụng từ layout tips:

- Code importable nên nằm trong `src/<package>/`.
- Root scripts nên là wrapper, không chứa logic chính.
- Có `paths.py` hoặc path resolver trung tâm.
- Không rải `Path(__file__).resolve().parents[...]` khắp repo.
- Runtime anchors như `.claude/`, `.hcom/`, `inputs/`, `outputs/`, `agentic/`, `schemas/` không nên move tùy hứng.

### 2.2. Progressive disclosure

Không nhét mọi thứ vào `CLAUDE.md`.

Mô hình context nên là:

```text
CLAUDE.md              # ngắn, entrypoint, dưới 200 dòng nếu có thể
.claude/rules/*.md     # rule theo vùng code
.claude/agents/*.md    # agent chuyên môn
.claude/skills/*       # workflow tái dùng
agentic/knowledge/*    # docs dài, chỉ đọc khi cần
agentic/memory/*       # memory curate
```

Lý do: context window là tài nguyên chung. File càng ngắn và đúng chỗ, agent càng ít lạc hướng.

### 2.3. Deterministic gates over vibes

Agent có thể sai. Gate bằng code ít sai hơn.

Những việc nên có script/hook:

- chặn đọc secrets,
- chặn command nguy hiểm,
- scan secrets,
- validate migration,
- run lint/test/build,
- validate memory card,
- validate generated output schema,
- log tool calls.

### 2.4. Agent roles phải có boundary

Đội agent không nên là nhiều prompt chung chung. Mỗi agent cần:

- nhiệm vụ rõ,
- tool access giới hạn,
- output contract rõ,
- stop condition rõ,
- khi nào được gọi rõ.

Ví dụ:

- `planner`: không edit file.
- `researcher`: chỉ đọc và gom evidence.
- `implementer`: edit theo plan đã rõ.
- `reviewer`: review diff, không tự sửa nếu chưa được yêu cầu.
- `security-reviewer`: bắt buộc khi chạm auth/secrets/db/infra.
- `memory-curator`: chỉ promote memory đã validated.

## 3. Generator Input Schema

Một skill/agent scaffold repo nên nhận các input sau:

```yaml
repo_mode: greenfield | existing_repo | retrofit_existing_agentic
target_runtime: claude_code | claude_code_plus_hcom | generic_agentic
os_profile: windows | wsl2 | linux | macos
language_stack:
  primary: python | typescript | mixed | unknown
  package_manager: npm | pnpm | uv | pip | poetry | unknown
product_layout:
  apps: true | false
  services: true | false
  packages: true | false
  db: true | false
  infra: true | false
risk_profile: low | standard | high
needs_mcp: true | false
needs_hooks: true | false
needs_memory_system: true | false
needs_eval_system: true | false
needs_src_layout: true | false
overwrite_policy: never | ask | allow_generated_only
validation_level: minimal | standard | strict
```

Nếu input thiếu, generator nên tự inspect repo trước khi hỏi:

- `git status --short`
- `rg --files`
- detect `package.json`, `pyproject.toml`, `pnpm-lock.yaml`, `uv.lock`
- detect existing `.claude/`, `CLAUDE.md`, `agentic/`, `scripts/gates/`
- detect high-risk folders: `db/`, `infra/`, `auth`, `secrets`, `.env`

## 4. Output Profiles

Generator nên hỗ trợ nhiều profile để không lúc nào cũng scaffold quá to.

### Profile A: Minimal Claude Baseline

Dùng khi repo nhỏ hoặc mới bắt đầu.

Tạo:

```text
CLAUDE.md
.claude/settings.json
.claude/rules/00-global.md
scripts/gates/run-quality-gate.*
scripts/gates/scan-secrets.*
agentic/README.md
agentic/memory/memory-candidates.md
```

Lý do: đủ để Claude có briefing, có permission baseline, có quality gate, có nơi ghi memory candidate.

### Profile B: Standard Agentic Team

Dùng cho repo đang phát triển thật.

Thêm:

```text
.claude/agents/planner.md
.claude/agents/researcher.md
.claude/agents/implementer.md
.claude/agents/reviewer.md
.claude/agents/qa.md
.claude/agents/security-reviewer.md
.claude/agents/lead-gatekeeper.md
.claude/skills/plan-task/SKILL.md
.claude/skills/review-pr/SKILL.md
.claude/skills/security-review/SKILL.md
.claude/skills/quality-gate/SKILL.md
agentic/knowledge/*
agentic/policies/*
agentic/orchestration/*
```

Lý do: đủ team roles và workflow để xử lý task vừa và lớn.

### Profile C: Full Governance / High Risk

Dùng khi repo có auth, billing, DB migration, production infra, hoặc external side effects.

Thêm:

```text
.claude/hooks/*
.claude/skills/memory-promote/SKILL.md
.claude/skills/write-adr/SKILL.md
agentic/evals/*
agentic/logs/.gitkeep
scripts/gates/validate-migration.py
scripts/gates/validate-memory-card.py
scripts/gates/validate-output-schema.py
.mcp.json
```

Lý do: high-risk repo cần enforcement, audit log, evals, ADR, memory discipline.

## 5. Canonical Folder Contract

### 5.1. Root files

```text
CLAUDE.md
CLAUDE.local.md
.mcp.json
.gitignore
```

Vai trò:

- `CLAUDE.md`: briefing mặc định cho Claude Code.
- `CLAUDE.local.md`: ghi chú local/private, gitignored.
- `.mcp.json`: tool gateway project-scoped.
- `.gitignore`: chặn secrets, local logs, settings local.

### 5.2. `.claude/`

```text
.claude/
  settings.json
  settings.local.example.json
  rules/
  agents/
  skills/
  hooks/
```

Vai trò:

- `settings.json`: permissions, hooks, env, runtime guardrails.
- `rules/`: rule theo global/path-specific context.
- `agents/`: subagents chuyên môn.
- `skills/`: workflow reusable.
- `hooks/`: deterministic enforcement trước/sau tool use.

### 5.3. `agentic/`

```text
agentic/
  README.md
  knowledge/
  memory/
  orchestration/
  policies/
  evals/
  logs/
```

Vai trò:

- `knowledge/`: kiến thức project ổn định.
- `memory/`: memory đã curate, tách candidate với durable.
- `orchestration/`: cách phối agent.
- `policies/`: approval, tool risk, data handling.
- `evals/`: regression/golden/red-team.
- `logs/`: trace local/generated.

### 5.4. `scripts/gates/`

```text
scripts/gates/
  run-quality-gate.sh
  scan-secrets.sh
  validate-migration.py
  validate-memory-card.py
  validate-output-schema.py
```

Vai trò:

- biến “nên kiểm tra” thành command deterministic,
- làm acceptance test cho agent,
- giúp reviewer/QA không phụ thuộc cảm giác.

### 5.5. `src/<package>/` nếu repo có code implementation

```text
src/<package>/
  paths.py
  cli/
  tools/
  gates/
```

Vai trò:

- code importable sống trong package rõ ràng,
- root scripts chỉ wrapper,
- path resolver giữ layout move được.

## 6. File-by-File Build Contract

### 6.1. `CLAUDE.md`

Phải chứa:

- project identity,
- repo map,
- operating modes,
- hard rules,
- common commands,
- memory policy,
- links tới knowledge/policy chính.

Không nên chứa:

- docs quá dài,
- toàn bộ architecture,
- secret,
- rule path-specific chi tiết,
- transcript dài.

Acceptance:

```text
[ ] Dưới khoảng 200 dòng nếu có thể
[ ] Có commands thật của repo
[ ] Có hard rules rõ
[ ] Có link tới agentic/knowledge và agentic/policies
[ ] Không import quá nhiều file dài bằng @path
```

### 6.2. `.claude/settings.json`

Phải chứa:

- `permissions.allow` cho command read-only và gate an toàn,
- `permissions.ask` cho install, commit, push, migrate, docker, deploy,
- `permissions.deny` cho `.env`, secrets, credential files, destructive shell,
- hooks nếu profile yêu cầu.

Acceptance:

```text
[ ] Chặn đọc .env/secrets
[ ] Chặn rm -rf/sudo/chmod 777/curl|sh
[ ] Ask trước git push/deploy/migrate/install
[ ] Hook paths tồn tại nếu được cấu hình
```

### 6.3. `.claude/rules/*.md`

Nên có:

```text
00-global.md
10-code-style.md
20-testing.md
30-security.md
40-git-workflow.md
backend/api-design.md
database/migration-rls.md
frontend/react-ui.md
infra/deployment.md
```

Rule tốt phải:

- ngắn,
- cụ thể,
- có `paths:` frontmatter nếu chỉ áp dụng cho vùng code,
- không lặp lại toàn bộ `CLAUDE.md`.

### 6.4. `.claude/agents/*.md`

Minimum team:

```text
lead-gatekeeper
planner
researcher
architect
implementer
reviewer
qa
security-reviewer
memory-curator
skill-maintainer
```

Mỗi agent cần:

```yaml
name:
description:
tools:
model:
permissionMode:
maxTurns:
```

Body cần:

- responsibilities,
- what not to do,
- workflow,
- output format,
- stop conditions.

### 6.5. `.claude/skills/*/SKILL.md`

Minimum skills:

```text
plan-task
inspect-codebase
implement-change
review-pr
security-review
quality-gate
write-adr
memory-promote
```

Skill tốt phải:

- frontmatter `name` và `description` rõ trigger,
- body ngắn, procedural,
- references/scripts/assets chỉ tạo khi thật cần,
- không tạo README phụ linh tinh trong skill folder,
- có examples/scripts nếu workflow cần deterministic output.

Theo nguyên tắc skill:

- `SKILL.md` là entrypoint, không phải encyclopedia.
- Detailed variants cho vào `references/`.
- Deterministic repeated logic cho vào `scripts/`.
- Templates cho vào `assets/` hoặc `templates/`.

### 6.6. Hooks

Recommended:

```text
block-dangerous-bash.sh
block-sensitive-read.sh
block-risky-write.py
log-tool-call.py
inject-quality-reminder.py
```

Hooks nên:

- đọc JSON từ stdin,
- trả JSON permission decision khi cần deny/ask,
- fail safe với protected paths,
- log vào `agentic/logs/`, không log secrets.

### 6.7. `agentic/memory/*`

Cần tách:

```text
memory-candidates.md   # staging, chưa authoritative
durable-facts.md       # facts đã validate
decisions.md           # decisions/ADR summary
gotchas.md             # lỗi hay gặp
failure-patterns.md    # pattern thất bại lặp lại
commands-and-recipes.md
incidents.md
```

Memory promotion rule:

```text
[ ] reusable
[ ] validated
[ ] non-secret
[ ] concise
[ ] source clear
```

## 7. Build Phases

### Phase 0: Inspect Existing Repo

Run read-only inventory:

```bash
git status --short
rg --files
```

Detect:

- stack,
- package manager,
- existing Claude config,
- existing docs,
- high-risk folders,
- current validation commands.

Reason: generator must adapt, not overwrite blindly.

### Phase 1: Claude Baseline

Create/update:

```text
CLAUDE.md
.gitignore
.claude/settings.json
.claude/rules/00-global.md
scripts/gates/run-quality-gate.*
scripts/gates/scan-secrets.*
```

Reason: before creating many agents, establish basic briefing and safety.

Validation:

```text
[ ] settings JSON parses
[ ] scripts/gates exist
[ ] .gitignore protects local/private files
```

### Phase 2: Agent Team

Create:

```text
.claude/agents/planner.md
.claude/agents/researcher.md
.claude/agents/implementer.md
.claude/agents/reviewer.md
.claude/agents/qa.md
.claude/agents/security-reviewer.md
.claude/agents/lead-gatekeeper.md
```

Reason: multi-agent setup only works if roles are explicit and bounded.

Validation:

```text
[ ] each agent has name/description
[ ] tools are minimal for role
[ ] reviewer/security agents do not edit by default
[ ] lead has routing/handoff contract
```

### Phase 3: Skills

Create:

```text
.claude/skills/plan-task/SKILL.md
.claude/skills/review-pr/SKILL.md
.claude/skills/security-review/SKILL.md
.claude/skills/quality-gate/SKILL.md
.claude/skills/write-adr/SKILL.md
.claude/skills/memory-promote/SKILL.md
```

Reason: skills turn repeated workflows into reusable operating procedures.

Validation:

```text
[ ] skill names are hyphen-case
[ ] frontmatter has name and description
[ ] description includes when to use
[ ] SKILL.md is concise
[ ] scripts/references only exist when useful
```

### Phase 4: Knowledge, Memory, Policy

Create:

```text
agentic/README.md
agentic/knowledge/project-overview.md
agentic/knowledge/system-map.md
agentic/knowledge/auth-permissions.md
agentic/memory/*
agentic/policies/approval-gates.md
agentic/policies/tool-risk-levels.md
agentic/policies/sensitive-files.md
agentic/orchestration/modes.md
agentic/orchestration/handoff-contracts.md
```

Reason: keep long-lived knowledge out of `CLAUDE.md`, but still easy to discover.

Validation:

```text
[ ] CLAUDE.md links to key files
[ ] candidate memory is separate from durable memory
[ ] approval gates list high-risk actions
```

### Phase 5: Hooks, MCP, Evals

Create when profile needs it:

```text
.claude/hooks/*
.mcp.json
agentic/evals/rubric-default.md
agentic/evals/golden-tasks/
agentic/evals/regression-cases/
agentic/evals/red-team/
agentic/logs/.gitkeep
```

Reason: mature repos need enforcement, external tools, and regression checks.

Validation:

```text
[ ] hooks executable on Linux/WSL
[ ] hooks fail safe
[ ] .mcp.json has no secrets
[ ] eval folders exist and scorecards are gitignored if generated
```

## 8. Generator Workflow

Một agent/skill dựng repo nên chạy quy trình này:

```text
1. Inspect repo
2. Select profile
3. Build file plan
4. Check overwrite conflicts
5. Create directories
6. Write minimal templates
7. Add stack-specific commands
8. Add settings/hooks/gates
9. Add docs index
10. Run validation
11. Report files created and next steps
```

Pseudo-contract:

```yaml
input:
  repo_path:
  profile:
  stack:
  overwrite_policy:
output:
  created_files:
  updated_files:
  skipped_files:
  conflicts:
  validation:
  next_steps:
```

## 9. Overwrite Policy

Default should be `never`.

Rules:

- If file exists, do not overwrite silently.
- If generated file exists and has marker, update only generated section.
- If user-owned file exists, append a proposed patch or create `.example`.
- For `.claude/settings.json`, merge conservatively and preserve existing permissions.
- For `.gitignore`, append missing lines, do not reorder the whole file.

Recommended generated marker:

```text
<!-- agentic-scaffold:start -->
...
<!-- agentic-scaffold:end -->
```

For JSON, use a top-level metadata key only if the target schema allows it. Otherwise avoid markers and do structural merge.

## 10. Stack-Specific Adaptation

### Python repo

Commands:

```bash
python -m py_compile ...
pytest
ruff check .
```

Recommended:

```text
src/<package>/paths.py
scripts/*.py wrappers
```

### TypeScript repo

Commands:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Recommended rules:

```text
.claude/rules/frontend/react-ui.md
.claude/rules/backend/api-design.md
```

### Mixed repo

Use layered gates:

```bash
bash scripts/gates/run-quality-gate.sh
```

Let that script call Python/Node-specific checks based on files present.

## 11. Validation Contract

Minimal validation:

```text
[ ] generated files exist
[ ] JSON files parse
[ ] shell/python scripts compile or syntax-check
[ ] no secrets committed
[ ] CLAUDE.md links are not broken
```

Standard validation:

```text
[ ] minimal validation
[ ] quality gate runs
[ ] agent files have valid frontmatter
[ ] skill files have name/description
[ ] hooks are executable or documented for Windows/WSL
```

Strict validation:

```text
[ ] standard validation
[ ] simulate blocked secret read
[ ] simulate blocked dangerous bash
[ ] run review-pr skill against current diff
[ ] run quality-gate skill
[ ] create one memory candidate and validate it
```

Rule-based structure validation:

```bash
python .docs/runbooks/new-claude-repo/validate_agentic_structure.py --profile minimal
python .docs/runbooks/new-claude-repo/validate_agentic_structure.py --profile standard
python .docs/runbooks/new-claude-repo/validate_agentic_structure.py --profile full --json
```

Quality scoring reference:

- See `claude_agentic_repo_quality_rubric.md` in this folder for the folder-level, file-level, and overall scoring rubric.
- Use the rule-based validator for deterministic structure checks.
- Use the rubric for qualitative review after the structure gate passes.

## 12. Failure Modes To Prevent

### 12.1. Giant CLAUDE.md

Problem: too much context loaded every session.

Fix:

- Keep `CLAUDE.md` short.
- Move details to `agentic/knowledge` or `.claude/rules`.

### 12.2. Agents with overlapping responsibilities

Problem: planner edits, reviewer fixes, security agent becomes general reviewer.

Fix:

- Add explicit “do not edit” rules.
- Restrict tools per agent.
- Require output contract.

### 12.3. Hooks that leak secrets

Problem: log hook records sensitive tool input.

Fix:

- Redact `.env`, tokens, passwords, secret-like values.
- Do not log file content for sensitive paths.

### 12.4. Path chaos after moving folders

Problem: scripts break because implementation paths changed.

Fix:

- Use wrapper scripts.
- Use package imports.
- Use central `paths.py`.
- Keep runtime anchors stable.

### 12.5. Scaffold overwrites user files

Problem: generator destroys custom config.

Fix:

- Default no overwrite.
- Merge carefully.
- Create `.example` if unsure.
- Report conflicts.

## 13. Suggested Skill Shape

Nếu biến blueprint này thành skill, tên nên là:

```text
claude-agentic-repo-scaffold
```

Skill frontmatter:

```yaml
---
name: claude-agentic-repo-scaffold
description: Scaffold or retrofit a Claude Code-native agentic repository with CLAUDE.md, .claude rules/agents/skills/settings/hooks, agentic knowledge/memory/policies/evals, validation gates, and move-safe src layout. Use when creating a new AI-agentic folder, upgrading an existing repo for Claude Code, or generating governance/workflow scaffolding for agent teams.
---
```

Recommended skill resources:

```text
claude-agentic-repo-scaffold/
  SKILL.md
  references/
    blueprint.md
    profiles.md
    file-contracts.md
    validation.md
  scripts/
    inspect_repo.py
    scaffold_agentic_repo.py
    validate_agentic_repo.py
  assets/
    templates/
      CLAUDE.md
      settings.json
      rules/
      agents/
      skills/
      agentic/
```

Why:

- `SKILL.md` stays lean.
- Detailed contracts live in references.
- Scaffold/validation are deterministic scripts.
- Templates are assets copied into target repo.

## 14. Suggested Agent Shape

Nếu biến thành subagent, tên nên là:

```text
agentic-repo-architect
```

Agent purpose:

```yaml
name: agentic-repo-architect
description: Use to design, scaffold, or retrofit a repository into a Claude Code-native agentic workspace with safe folder layout, .claude configuration, agent team roles, reusable skills, hooks, memory, policies, and validation gates.
tools: Read, Grep, Glob, Bash, Write, Edit
permissionMode: default
```

Agent workflow:

```text
1. Inspect current repo.
2. Detect stack and existing agentic assets.
3. Choose minimal/standard/full profile.
4. Produce scaffold plan.
5. Create files without overwriting user-owned files.
6. Add validation gates.
7. Run validation.
8. Report created/updated/skipped/conflicts.
```

Stop conditions:

```text
- Existing files conflict and overwrite_policy is not explicit.
- Repo contains secrets or production config in target paths.
- Hooks/settings would block current repo's known valid workflow.
- Validation fails in a way that requires product-specific decision.
```

## 15. Suggested AI Tool / CLI Shape

Nếu tạo CLI/tool generator:

```bash
agentic-scaffold init --profile standard --target claude-code
agentic-scaffold inspect
agentic-scaffold validate
agentic-scaffold add-skill review-pr
agentic-scaffold add-agent security-reviewer
```

Core commands:

```text
inspect    # read-only repo detection
plan       # output file plan
init       # create scaffold
retrofit   # adapt existing repo
validate   # check generated system
doctor     # explain missing/weak pieces
```

Safety defaults:

- no overwrite,
- dry-run first for existing repos,
- generated move log,
- validation after every mutation,
- no secrets in output.

## 16. Acceptance Checklist

Repo được coi là Claude-native agentic baseline khi:

```text
[ ] CLAUDE.md exists and is concise
[ ] .claude/settings.json exists and blocks secrets/destructive commands
[ ] .claude/rules has global and at least one stack/path rule
[ ] .claude/agents has planner/researcher/implementer/reviewer/qa/security/lead
[ ] .claude/skills has plan/review/security/quality/memory workflows
[ ] scripts/gates has quality and secret scan
[ ] agentic/knowledge has project/system/auth maps
[ ] agentic/memory separates candidates from durable memory
[ ] agentic/policies has approval gates and sensitive file policy
[ ] hooks exist or are intentionally skipped by profile
[ ] .mcp.json exists or is intentionally skipped
[ ] validation commands run or failure is documented
[ ] existing user files were not overwritten silently
```

Recommended final review output:

```yaml
structure_gate:
  command:
  score:
  readiness:
  missing:
rubric_review:
  overall_score:
  folder_scores:
  file_scores:
  hard_gates_failed:
required_fixes:
optional_improvements:
evidence:
```

## 17. The One-Sentence Rule

Khi dựng repo agentic cho Claude Code:

> `CLAUDE.md` tells Claude how to think, `.claude/` gives Claude team members and workflows, `agentic/` stores durable knowledge and governance, `scripts/gates/` enforces reality, and `src/` keeps implementation movable.
