# Observability — log, trace, audit

Làm sao biết được mỗi thành phần bên trong đang làm gì, để tối ưu.

## Structure

```
observability/
├── traces/
│   ├── agent_runs/      # one JSON per (input_id, stage, version) — what the agent did
│   ├── tool_calls/      # one JSON per tool invocation — what was called, with what input/output
│   ├── memory_reads/    # which files / learnings / schemas the agent loaded at session start
│   ├── memory_writes/   # which artifacts the agent wrote
│   ├── gates/           # which gates fired, pass/fail, evidence
│   └── approvals/       # human-in-the-loop decisions (when an agent halts and asks)
├── dashboards/          # aggregate views (built from traces/)
├── failure-taxonomy.md  # canonical list of failure modes + how each is detected + handled
└── audit-log-schema.md  # the canonical trace schema (Draft-7)
```

## Trace schema

```json
{
  "run_id": "run-2026-06-01-001",
  "task": "Add payment webhook endpoint",
  "lead_agent": "backend-lead",
  "agents_called":   ["planner", "implementer", "qa", "security"],
  "tools_used":      ["read_file", "write_file", "run_tests"],
  "memory_read":     ["mem-payment-architecture", "mem-webhook-security"],
  "memory_write":    ["outputs/<id>/04_synthesize/v1.json"],
  "gates": {
    "plan_gate":      "pass",
    "test_gate":      "pass",
    "security_gate":  "fail",
    "json_schema":    "pass",
    "llm_judge":      "pass"
  },
  "approvals":       [{"at": "...", "decision": "revise_plan", "by": "human"}],
  "final_status":    "blocked",
  "reason":          "Missing signature verification"
}
```

See `audit-log-schema.md` for the machine-readable form.

## Tools

- `tools/trace.py` — append a trace event; called by the orchestrator + every stage agent.
- `tools/observability/render_dashboard.py` — read all traces for a run_id, emit a dashboard JSON.

## Conventions

- Every trace event = 1 JSON file in the right `traces/<bucket>/` dir.
- Filename = `<run_id>__<stage>__<version>.json` (e.g. `run-001__02_extract__v1.json`).
- One run_id per `input_id` end-to-end (across all 6 stages).
- Append-only; no in-place edits.
- gitignored; rotated to `observability/archive/<month>/` monthly.
