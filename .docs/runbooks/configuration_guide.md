# Auto-Research Pipeline Configuration Guide

This guide details all configuration points for the `auto-research` workspace, allowing you to tailor the pipeline's execution, budgets, validation thresholds, permissions, and agent characteristics.

---

## 📋 1. `pipeline.json`

The central source of truth (`pipeline.json`) defines stages, budgets, validation limits, and skill setups.

### Top-Level Budgets
```json
"budgets": {
  "max_retries_per_stage": 3,
  "max_total_tool_calls": 50,
  "max_wall_time_minutes": 60,
  "max_context_tokens": 180000
}
```
*   `max_retries_per_stage`: Maximum number of times the orchestrator will retry a stage before halting.
*   `max_total_tool_calls`: Cumulative ceiling on the number of tool invocations allowed for the entire run.
*   `max_wall_time_minutes`: Hard limit on the wall-clock execution time for a complete run.
*   `max_context_tokens`: Maximum context window tokens.

### Stages Configurations
Under `stages[]`:
*   `id`: Stage identifier (e.g., `00_research`, `02_extract`).
*   `name`: Plaintext stage name.
*   `agent`: The short name of the agent responsible for this stage.
*   `schema`: Path to the JSON Schema (Draft-7) that validated output must match.
*   `output_format`: Format suffix (e.g. `json`, `txt`, `json+md`).
*   `max_options`: Number of candidate options to generate (default `1` for sequential; `3` for multi-option extraction).
*   `execution_mode`: Execution mode. Set to `"parallel"` to process options (A, B, C) concurrently.
*   `skill_triggers`: An array of progressive skill keys (e.g. `["web-search"]`, `["markdown-report"]`) loaded on-demand.

### Critic Configurations
```json
"critic": {
  "agent": "critic",
  "checks": ["schema", "completeness", "llm_judge", "evidence_grounding"],
  "llm_judge_threshold": 0.7
}
```
*   `checks`: List of active validations (`schema` validation, `completeness` checks, `llm_judge` heuristics, `evidence_grounding` tests).
*   `llm_judge_threshold`: Score (0.0 to 1.0) below which the Critic rejects the output and triggers a retry.

---

## 🔒 2. `.env` (Environment Variables)

Located at the repository root (copy from `.env.example`):
*   `SLACK_WEBHOOK`: (Optional) Slack webhook URL. Set to receive instant completion or error notifications.
*   `HCOM_TAG`: (Optional) Overrides the default `hcom` Swarm tag (default: `research-pipeline`).

---

## 🛡️ 3. `.claude/settings.json` (Claude Permissions & Hooks)

Defines security scopes and command-execution hooks.
*   `permissions.allow`: Tool allowlist for terminal calls (e.g. `Bash(hcom:*)`, `Bash(uv run python -m tools.*)`). Modify this if you add new python helper scripts or custom CLI commands to ensure agent authorization.
*   `hooks`: Configures hooks triggered at `SessionStart`, `PreToolUse`, `PostToolUse`, etc. Do not edit this manually; run `hcom hooks add` to auto-install lifecycle hooks.

---

## 🤖 4. Agent Profiles (`.claude/agents/*.{json,md}`)

Every agent (Orchestrator, Researcher, Ingestor, Extractor, Analyzer, Synthesizer, Critic, Formatter) is configured via matching `.json` and `.md` profiles:
*   `*.json`: Declares allowed tools, purpose, and trigger patterns (inbound/outbound handoff formats).
*   `*.md`: Instructs the agent on execution behavior (Ralph Wiggum state recovery loop, depth rules, claiming criteria, formatting specifications, etc.). Update these system-prompt instructions to fine-tune individual agent behaviors.

---

## 📐 5. Artifact Schemas (`schemas/*.json`)

The structural shapes of all intermediate and final outputs are strictly enforced using JSON Schema.
*   `00_research.json` to `05_format.json`: Define required properties, types, array structures, and regex patterns for the output of each pipeline stage. If you need to add new data fields (e.g., semantic tags or custom lists), modify these schemas first; the Critic will automatically block invalid structures.

---

## 🚪 6. Validation Gates (`gates/`)

Quality control checkpoints run pre-dispatch, post-execution, and during plan formulation:
*   `input-gates/`: Checklist validation constraints before accepting an incoming input.
*   `output-gates/`: Heuristics executed on stage deliverables before finalizing them on disk.
*   `plan-gates/`: Rules for verification of the execution task plans.
*   `release-gates/`: Checks running before marking a pipeline run as complete.

