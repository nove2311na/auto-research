#!/usr/bin/env python3
"""render_scorecard.py — pretty-print a scorecard to the terminal.

Usage:
    python -m research_pipeline.tools.evals.render_scorecard <scorecard.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m tools.evals.render_scorecard <scorecard.json>", file=sys.stderr)
        sys.exit(1)

    card_path = Path(sys.argv[1])
    if not card_path.exists():
        print(f"Error: scorecard file not found: {card_path}", file=sys.stderr)
        sys.exit(1)

    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error: failed to parse scorecard: {e}", file=sys.stderr)
        sys.exit(1)

    run_id = card.get("run_id", "unknown")
    agent = card.get("agent", "unknown")
    task = card.get("task", "unknown")
    scores = card.get("rubric_scores", {})
    final_score = card.get("final_score", 0.0)
    gates = card.get("gates", {})
    evidence = card.get("evidence", [])
    status = card.get("final_status", "fail").upper()

    print("=" * 70)
    print(f"  EVALUATION SCORECARD: {run_id}")
    print("=" * 70)
    print(f"  Task/Topic:  {task}")
    print(f"  Agent:       {agent}")
    print(f"  Status:      {status}")
    print(f"  Final Score: {final_score:.4f}")
    print()

    print("-" * 70)
    print("  Rubric Criteria Scores")
    print("-" * 70)
    for criterion, score in sorted(scores.items()):
        bar = "#" * int(round(score * 20))
        spaces = " " * (20 - len(bar))
        print(f"  - {criterion:<16}: {score:.4f}  [{bar}{spaces}]")
    print()

    if gates:
        print("-" * 70)
        print("  Gates Status")
        print("-" * 70)
        for gate_name, gate_status in sorted(gates.items()):
            print(f"  - {gate_name:<16}: {str(gate_status).upper()}")
        print()

    if evidence:
        print("-" * 70)
        print("  Evidence / Reference Links")
        print("-" * 70)
        for ev in evidence:
            print(f"  - {ev}")
        print()

    print("=" * 70)

if __name__ == "__main__":
    main()
