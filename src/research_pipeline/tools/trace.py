"""trace.py — append a trace event to observability/traces/<bucket>/.

Usage:
    python -m tools.trace log agent_run --run-id run-2026-06-01-001 --stage 02_extract --data '{...}'
    python -m tools.trace log gate --run-id run-001 --gate json_schema --status pass
    python -m tools.trace log final --run-id run-001 --status pass --reason "all gates passed"

Buckets: agent_runs | tool_calls | memory_reads | memory_writes | gates | approvals
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

from research_pipeline.paths import OBSERVABILITY, REPO_ROOT

REPO = REPO_ROOT
TRACES = OBSERVABILITY / "traces"

VALID_BUCKETS = ["agent_runs", "tool_calls", "memory_reads", "memory_writes", "gates", "approvals"]


def _write(bucket: str, run_id: str, suffix: str, payload: dict[str, Any]) -> Path:
    if bucket not in VALID_BUCKETS:
        raise ValueError(f"invalid bucket: {bucket}; valid: {VALID_BUCKETS}")
    d = TRACES / bucket
    d.mkdir(parents=True, exist_ok=True)
    safe_suffix = suffix.replace("/", "_").replace(" ", "_")
    path = d / f"{run_id}__{safe_suffix}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def log_agent_run(args: argparse.Namespace) -> int:
    payload = {
        "run_id": args.run_id,
        "task": args.task or "",
        "lead_agent": args.lead_agent or "orchestrator",
        "agents_called": args.agents_called or [],
        "tools_used": args.tools_used or [],
        "memory_read": args.memory_read or [],
        "memory_write": args.memory_write or [],
        "stage": args.stage,
        "version": args.version,
        "final_status": args.status or "pass",
    }
    p = _write("agent_runs", args.run_id, f"{args.stage}__v{args.version}", payload)
    print(f"wrote {p}")
    return 0


def log_gate(args: argparse.Namespace) -> int:
    payload = {
        "run_id": args.run_id,
        "gate": args.gate,
        "status": args.status,
        "evidence": args.evidence or [],
    }
    p = _write("gates", args.run_id, args.gate, payload)
    print(f"wrote {p}")
    return 0


def log_final(args: argparse.Namespace) -> int:
    payload = {
        "run_id": args.run_id,
        "task": args.task or "",
        "lead_agent": "orchestrator",
        "final_status": args.status,
        "reason": args.reason or "",
    }
    p = _write("agent_runs", args.run_id, "final", payload)
    print(f"wrote {p}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append a trace event")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ar = sub.add_parser("agent_run")
    p_ar.add_argument("--run-id", required=True)
    p_ar.add_argument("--stage", required=True)
    p_ar.add_argument("--version", required=True, type=int)
    p_ar.add_argument("--task")
    p_ar.add_argument("--lead-agent")
    p_ar.add_argument("--agents-called", nargs="*")
    p_ar.add_argument("--tools-used", nargs="*")
    p_ar.add_argument("--memory-read", nargs="*")
    p_ar.add_argument("--memory-write", nargs="*")
    p_ar.add_argument("--status", default="pass")
    p_ar.set_defaults(func=log_agent_run)

    p_g = sub.add_parser("gate")
    p_g.add_argument("--run-id", required=True)
    p_g.add_argument("--gate", required=True)
    p_g.add_argument("--status", required=True, choices=["pass", "fail", "skip"])
    p_g.add_argument("--evidence", nargs="*")
    p_g.set_defaults(func=log_gate)

    p_f = sub.add_parser("final")
    p_f.add_argument("--run-id", required=True)
    p_f.add_argument("--status", required=True, choices=["pass", "warn", "fail", "blocked"])
    p_f.add_argument("--task")
    p_f.add_argument("--reason")
    p_f.set_defaults(func=log_final)

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return cast(int, args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
