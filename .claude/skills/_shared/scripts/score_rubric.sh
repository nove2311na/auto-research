#!/usr/bin/env bash
# score_rubric.sh — apply the 8-criterion rubric to a run; emit a scorecard.
#
# Usage: score_rubric.sh <input_id> [<case-json>]
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id> [<case-json>]}"
CASE="${2:-}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

if [ -n "$CASE" ] && [ -f "$CASE" ]; then
    uv run python -m tools.evals.run_eval "$CASE"
else
    # Default: use the qec-pipeline golden task
    uv run python -m tools.evals.run_eval evals/golden-tasks/qec-pipeline.json
fi
