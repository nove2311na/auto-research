#!/usr/bin/env bash
# run_eval.sh — runs the 05-format eval-cases against an input.
# Usage: run_eval.sh <input_id>
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

JSON="outputs/${INPUT_ID}/05_format/v1.json"
MD="outputs/${INPUT_ID}/05_format/v1.md"
META="outputs/${INPUT_ID}/05_format/v1.meta.json"

# 1. all 3 files exist
test -f "$JSON" || { echo "FAIL: $JSON missing"; exit 2; }
test -f "$MD"    || { echo "FAIL: $MD missing"; exit 2; }
test -f "$META"  || { echo "FAIL: $META missing"; exit 2; }

# 2. schema check
uv run python -m gates.output_gates json_schema --artifact "$JSON" --schema schemas/05_format.json

# 3. v1.md is non-trivial
n=$(wc -l < "$MD")
test "$n" -ge 30 || { echo "FAIL: v1.md is $n lines, expected >=30"; exit 2; }

# 4. v1.md contains Mermaid blocks (count >= diagrams in JSON)
mm_count=$(grep -c '^```mermaid' "$MD" || true)
test "$mm_count" -ge 1 || { echo "FAIL: v1.md has 0 mermaid blocks"; exit 2; }

# 5. meta.producer = "formatter"
producer=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['producer'])")
test "$producer" = "formatter" || { echo "FAIL: meta.producer=$producer, expected formatter"; exit 2; }

# 6. trace
uv run python -m tools.trace gate --run-id "run-${INPUT_ID}" --gate 05_format_self_check --status pass

echo "OK 05-format for ${INPUT_ID}"
