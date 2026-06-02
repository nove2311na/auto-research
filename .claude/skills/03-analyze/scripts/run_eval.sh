#!/usr/bin/env bash
# run_eval.sh — runs the 03-analyze eval-cases against an input.
# Usage: run_eval.sh <input_id>
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

ART="outputs/${INPUT_ID}/03_analyze/v1.json"

# 1. json schema check
uv run python -m gates.output_gates json_schema --artifact "$ART" --schema schemas/03_analyze.json

# 2. themes 2-6
n=$(uv run python -c "import json; print(len(json.load(open('$ART', encoding='utf-8'))['themes']))")
test "$n" -ge 2 && test "$n" -le 6 || { echo "FAIL: themes=$n, expected 2-6"; exit 2; }

# 3. gaps 1-5
n=$(uv run python -c "import json; print(len(json.load(open('$ART', encoding='utf-8'))['gaps']))")
test "$n" -ge 1 && test "$n" -le 5 || { echo "FAIL: gaps=$n, expected 1-5"; exit 2; }

# 4. contradictions 0-3
n=$(uv run python -c "import json; print(len(json.load(open('$ART', encoding='utf-8'))['contradictions']))")
test "$n" -le 3 || { echo "FAIL: contradictions=$n, expected 0-3"; exit 2; }

# 5. trace
uv run python -m tools.trace gate --run-id "run-${INPUT_ID}" --gate 03_analyze_self_check --status pass

echo "OK 03-analyze for ${INPUT_ID}"
