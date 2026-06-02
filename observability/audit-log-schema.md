# Audit log schema (canonical)

Draft-7 schema for `observability/traces/**/*.json`. See `audit-log.schema.json` for the machine form.

## Required fields

| Field | Type | Description |
|---|---|---|
| `run_id` | string (pattern `^run-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3,}$`) | One per `input_id` end-to-end run. |
| `task` | string (minLength 1) | One-sentence description of the task. |
| `lead_agent` | string (enum: the 8 agent names) | The agent that orchestrated the work. |
| `agents_called` | array of strings (enum: 8 agent names) | All agents invoked during the run. |
| `tools_used` | array of strings (minLength 0) | All tools called. |
| `memory_read` | array of strings (file paths or memory ids) | What the agents loaded. |
| `memory_write` | array of strings (file paths) | What the agents persisted. |
| `gates` | object (see below) | Gate pass/fail per gate. |
| `approvals` | array of {at, decision, by} | HITL decisions. |
| `final_status` | enum: pass \| warn \| fail \| blocked | End state. |
| `reason` | string | One-sentence why. |

## Gates block (per run)

```json
{
  "input_completeness": "pass|fail|skip",
  "plan_review":        "pass|fail|skip",
  "json_schema":        "pass|fail|skip",
  "completeness":       "pass|fail|skip",
  "llm_judge":          "pass|fail|skip",
  "path_safety":        "pass|fail|skip",
  "manifest_consistency":"pass|fail|skip"
}
```

`skip` = gate not applicable for this run.

## Bucket conventions

- `traces/agent_runs/<run_id>__<stage>__<version>.json` — what an agent did for one stage+version.
- `traces/tool_calls/<run_id>__<tool>__<seq>.json` — one tool call.
- `traces/memory_reads/<run_id>__<agent>__<seq>.json` — what was loaded at session start.
- `traces/memory_writes/<run_id>__<agent>__<path_hash>.json` — what was written.
- `traces/gates/<run_id>__<gate_name>.json` — gate evidence.
- `traces/approvals/<run_id>__<seq>.json` — human decision.

## Lifecycle

1. Agent finishes writing an artifact → `tools/trace.py log memory_write` → emits file in `memory_writes/`.
2. Gate fires (PreToolUse hook) → emits file in `gates/`.
3. Stage completes → `tools/trace.py log agent_run` with the trace.
4. Critic scores → `tools/trace.py log tool_call` for the LLM-judge call.
5. Orchestrator halts → `tools/trace.py log approval` with the halt reason.
6. End of run → orchestrator emits a final aggregated trace at `traces/agent_runs/<run_id>__final.json`.
