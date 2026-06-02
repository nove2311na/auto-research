"""render_dashboard.py — aggregate trace logs and render a Swarm Execution Dashboard.

Usage:
    python -m research_pipeline.tools.observability.render_dashboard <run_id> [--output <path>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from research_pipeline.paths import OBSERVABILITY, OUTPUTS, REPO_ROOT

TRACES = OBSERVABILITY / "traces"


def aggregate_traces(run_id: str) -> dict[str, Any]:
    """Find and aggregate all traces matching the given run_id."""
    data: dict[str, Any] = {
        "run_id": run_id,
        "agent_runs": [],
        "gates": [],
        "tool_calls": [],
        "memory_reads": [],
        "memory_writes": [],
        "approvals": [],
        "performance": [],
        "summary": {
            "total_agent_runs": 0,
            "total_tool_calls": 0,
            "total_tokens_used": 0,
            "total_duration_ms": 0,
            "gates_passed": 0,
            "gates_failed": 0,
            "final_status": "unknown",
        }
    }

    # 1. Search in observability/traces/
    if TRACES.exists():
        for bucket in ["agent_runs", "gates", "tool_calls", "memory_reads", "memory_writes", "approvals"]:
            bucket_dir = TRACES / bucket
            if not bucket_dir.exists():
                continue
            # Search files that start with {run_id}__ or {run_id}_ or exactly {run_id}.json
            for p in bucket_dir.iterdir():
                if p.is_file() and p.suffix == ".json":
                    match = False
                    if p.name.startswith(f"{run_id}__") or p.name.startswith(f"{run_id}_") or p.name == f"{run_id}.json":
                        match = True
                    else:
                        # Fallback: check content
                        try:
                            content = json.loads(p.read_text(encoding="utf-8"))
                            if content.get("run_id") == run_id:
                                match = True
                        except Exception:
                            pass
                    
                    if match:
                        try:
                            item = json.loads(p.read_text(encoding="utf-8"))
                            data[bucket].append(item)
                        except Exception:
                            pass

    # 2. Read performance from outputs/<run_id>/trace.jsonl
    trace_file = OUTPUTS / run_id / "trace.jsonl"
    if trace_file.exists():
        try:
            for line in trace_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    perf_item = json.loads(line)
                    data["performance"].append(perf_item)
                    data["summary"]["total_tokens_used"] += perf_item.get("tokens_used", 0)
                    data["summary"]["total_tool_calls"] += perf_item.get("tool_calls_count", 0)
                    data["summary"]["total_duration_ms"] += perf_item.get("duration_ms", 0)
        except Exception:
            pass

    # 3. Calculate extra stats
    data["summary"]["total_agent_runs"] = len(data["agent_runs"])
    
    # Process gates
    for g in data["gates"]:
        status = g.get("status")
        if status == "pass":
            data["summary"]["gates_passed"] += 1
        elif status == "fail":
            data["summary"]["gates_failed"] += 1

    # Check final status
    for run in data["agent_runs"]:
        if "final" in run.get("run_id", "") or run.get("final_status"):
            data["summary"]["final_status"] = run.get("final_status", "unknown")
            break
            
    return data


def render_cli_dashboard(data: dict[str, Any]) -> None:
    """Print a beautiful CLI dashboard."""
    run_id = data["run_id"]
    sum_data = data["summary"]
    
    print("=" * 60)
    print(f" SWARM EXECUTION DASHBOARD: {run_id}")
    print("=" * 60)
    print(f"  Final Swarm Status :  {sum_data['final_status'].upper()}")
    print(f"  Total Run Duration :  {sum_data['total_duration_ms'] / 1000:.2f} s")
    print(f"  Total LLM Tokens   :  {sum_data['total_tokens_used']:,} tokens")
    print(f"  Est. Cost (USD)    :  ${(sum_data['total_tokens_used'] / 1_000_000) * 5.00:.4f}")
    print(f"  Agent Runs Count   :  {sum_data['total_agent_runs']}")
    print(f"  Total Tool Calls   :  {sum_data['total_tool_calls']}")
    print("-" * 60)
    
    print("  STAGES PERFORMANCE:")
    if data["performance"]:
        for perf in data["performance"]:
            stage = perf.get("stage", "unknown")
            dur = perf.get("duration_ms", 0) / 1000
            tok = perf.get("tokens_used", 0)
            tc = perf.get("tool_calls_count", 0)
            print(f"    - {stage:<15}: {dur:6.2f}s | {tok:7,} tokens | {tc:3} tools")
    else:
        print("    No performance metrics available (trace.jsonl missing or empty).")
    print("-" * 60)

    print("  GATES EVALUATION:")
    gates = data["gates"]
    if gates:
        for g in gates:
            gate_name = g.get("gate", "unknown")
            status = g.get("status", "unknown").upper()
            status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
            evidence = ", ".join(g.get("evidence", []))[:40]
            evidence_str = f" ({evidence}...)" if evidence else ""
            print(f"    - {gate_name:<20}: {status_icon}{evidence_str}")
    else:
        print("    No gate execution logs found.")
    print("-" * 60)

    print("  AGENT RUNS DETAILED:")
    agent_runs = data["agent_runs"]
    if agent_runs:
        for r in agent_runs:
            stage = r.get("stage", "final")
            lead = r.get("lead_agent", "unknown")
            status = r.get("final_status", "unknown").upper()
            status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WAIT]"
            print(f"    {status_icon} [{stage}] lead={lead}")
    else:
        print("    No agent run execution logs found.")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a trace-based dashboard.")
    parser.add_argument("run_id", help="The run_id/input_id to analyze")
    parser.add_argument("--output", help="Optional path to save the aggregated JSON dashboard")
    
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    
    try:
        aggregated = aggregate_traces(args.run_id)
        render_cli_dashboard(aggregated)
        
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(aggregated, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\nWrote aggregated dashboard JSON to {out_path}")
            
        return 0
    except Exception as e:
        print(f"Error rendering dashboard: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
