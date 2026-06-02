#!/usr/bin/env bash
# run_eval.sh — runs the 00-research eval-cases against an input.
# Usage: run_eval.sh <input_id>
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

# 1. json_schema_gate
uv run python -m gates.output_gates json_schema \
    --artifact "outputs/${INPUT_ID}/00_research/v1.json" \
    --schema    "schemas/00_research.json"

# 2. self_check
SKILL_DIR=".claude/skills/00-research"
META="outputs/${INPUT_ID}/00_research/v1.meta.json"
test -f "$META" || { echo "FAIL: meta missing"; exit 2; }
status=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['validation']['status'])")
test "$status" = "pending" || { echo "FAIL: status=$status"; exit 2; }

# 3. self-check 1: topic must be 1 sentence
topic=$(uv run python -c "import json; print(json.load(open('outputs/${INPUT_ID}/00_research/v1.json', encoding='utf-8'))['topic'])")
sent_count=$(echo "$topic" | grep -oE '[.!?]' | wc -l)
test "$sent_count" -le 2 || { echo "FAIL: topic must be 1-2 sentences"; exit 2; }

# 4. self-check 2: key_findings >= 3
kf_count=$(uv run python -c "import json; print(len(json.load(open('outputs/${INPUT_ID}/00_research/v1.json', encoding='utf-8'))['key_findings']))")
test "$kf_count" -ge 3 || { echo "FAIL: key_findings=$kf_count, expected >=3"; exit 2; }

# 5. trace
uv run python -m tools.trace gate \
    --run-id "run-${INPUT_ID}" \
    --gate 00_research_self_check \
    --status pass

echo "OK 00-research for ${INPUT_ID}"
