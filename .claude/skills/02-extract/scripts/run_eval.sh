#!/usr/bin/env bash
# run_eval.sh — runs the 02-extract eval-cases against an input.
# Usage: run_eval.sh <input_id>
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

# 1. read max_options dynamically
max_options=$(uv run python -c "import json; print(next((s.get('max_options', 3) for s in json.load(open('pipeline.json'))['stages'] if s['id'] == '02_extract'), 3))")

# 2. check option file existence
if [ "$max_options" -ge 1 ]; then
    test -f "outputs/${INPUT_ID}/02_extract/options/A/v1.json" || { echo "FAIL: option A missing"; exit 2; }
fi
if [ "$max_options" -ge 2 ]; then
    test -f "outputs/${INPUT_ID}/02_extract/options/B/v1.json" || { echo "FAIL: option B missing"; exit 2; }
fi
if [ "$max_options" -ge 3 ]; then
    test -f "outputs/${INPUT_ID}/02_extract/options/C/v1.json" || { echo "FAIL: option C missing"; exit 2; }
fi

# 3. each option matches the schema
for opt in A B C; do
    p="outputs/${INPUT_ID}/02_extract/options/${opt}/v1.json"
    [ -f "$p" ] || continue
    uv run python -m gates.output_gates json_schema --artifact "$p" --schema schemas/02_extract.json
done

# 4. differentiate options if max_options >= 2
if [ "$max_options" -ge 2 ]; then
    ent_a=$(uv run python -c "import json; print(len(json.load(open('outputs/${INPUT_ID}/02_extract/options/A/v1.json', encoding='utf-8'))['entities']))")
    ent_b=$(uv run python -c "import json; print(len(json.load(open('outputs/${INPUT_ID}/02_extract/options/B/v1.json', encoding='utf-8'))['entities']))")
    fa_a=$(uv run python -c "import json; print(len(json.load(open('outputs/${INPUT_ID}/02_extract/options/A/v1.json', encoding='utf-8'))['facts']))")
    fa_b=$(uv run python -c "import json; print(len(json.load(open('outputs/${INPUT_ID}/02_extract/options/B/v1.json', encoding='utf-8'))['facts']))")
    test "$ent_a" -gt "$ent_b" || { echo "FAIL: option A should be entity-dominant (A=$ent_a B=$ent_b)"; exit 2; }
    test "$fa_b" -ge "$fa_a" || { echo "FAIL: option B should be fact-dominant (A=$fa_a B=$fa_b)"; exit 2; }
fi

# 4. critic picked a winner: stage-root v1.json exists
test -f "outputs/${INPUT_ID}/02_extract/v1.json" || { echo "FAIL: critic did not pick a winner"; exit 2; }

# 5. trace
uv run python -m tools.trace gate \
    --run-id "run-${INPUT_ID}" \
    --gate 02_extract_self_check \
    --status pass

echo "OK 02-extract for ${INPUT_ID}"
