#!/usr/bin/env python3
"""run_suite.py — runs all evaluation cases in the workspace.

Usage:
    python -m research_pipeline.tools.evals.run_suite
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from research_pipeline.paths import EVALS, REPO_ROOT, SRC_ROOT

REPO = REPO_ROOT
SCORECARDS = EVALS / "scorecards"

def main() -> None:
    # 1. Discover all evaluation cases
    case_dirs = [EVALS / "golden-tasks", EVALS / "regression-cases"]
    case_files = []
    for d in case_dirs:
        if d.exists():
            case_files.extend(sorted(d.glob("*.json")))

    if not case_files:
        print("No evaluation cases found.", file=sys.stderr)
        sys.exit(0)

    print(f"Discovered {len(case_files)} evaluation cases.")
    print("Running evaluation suite...")
    print("=" * 80)

    results = []
    for case_file in case_files:
        print(f"Running case: {case_file.name}...")
        cmd = [sys.executable, "-m", "research_pipeline.tools.evals.run_eval", str(case_file)]
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{SRC_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print(f"  [ERROR] run_eval.py failed for {case_file.name}: {r.stderr.strip() or r.stdout.strip()}", file=sys.stderr)

        try:
            case_data = json.loads(case_file.read_text(encoding="utf-8"))
            run_id = case_data.get("id", case_file.stem)
            card_file = SCORECARDS / f"{run_id}.json"
            if card_file.exists():
                card = json.loads(card_file.read_text(encoding="utf-8"))
                results.append(card)
                print(f"  Result: {card['final_status'].upper()} (score: {card['final_score']:.4f})")
            else:
                print(f"  [FAIL] Scorecard not found for {run_id}", file=sys.stderr)
                results.append({
                    "run_id": run_id,
                    "final_score": 0.0,
                    "final_status": "fail",
                    "task": case_data.get("topic", "unknown"),
                    "error": "Scorecard not found"
                })
        except Exception as e:
            print(f"  [ERROR] Failed to parse case or scorecard: {e}", file=sys.stderr)

    print("=" * 80)
    print("Evaluation Summary:")
    print(f"{'Case ID':<30} | {'Task/Topic':<30} | {'Score':<8} | {'Status':<6}")
    print("-" * 80)

    total_score = 0.0
    passed_count = 0
    warned_count = 0
    failed_count = 0

    for r in results:
        run_id = r.get("run_id", "unknown")
        task = r.get("task", "unknown")
        if len(run_id) > 30:
            run_id = run_id[:27] + "..."
        if len(task) > 30:
            task = task[:27] + "..."

        score = r.get("final_score", 0.0)
        status = r.get("final_status", "fail")

        print(f"{run_id:<30} | {task:<30} | {score:<8.4f} | {status.upper():<6}")

        total_score += score
        if status == "pass":
            passed_count += 1
        elif status == "warn":
            warned_count += 1
        else:
            failed_count += 1

    avg_score = total_score / len(results) if results else 0.0
    print("-" * 80)
    print(f"Total: {len(results)} cases | Passed: {passed_count} | Warned: {warned_count} | Failed: {failed_count}")
    print(f"Overall Average Score: {avg_score:.4f}")

    # Save aggregate scorecard
    aggregate = {
        "total_cases": len(results),
        "passed": passed_count,
        "warned": warned_count,
        "failed": failed_count,
        "average_score": avg_score,
        "results": results
    }
    agg_file = SCORECARDS / "aggregate.json"
    agg_file.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved aggregate scorecard to {agg_file}")

    if failed_count > 0:
        print("Suite result: FAIL (one or more cases failed)", file=sys.stderr)
        sys.exit(1)
    else:
        print("Suite result: SUCCESS (all cases passed or warned)")
        sys.exit(0)

if __name__ == "__main__":
    main()
