#!/usr/bin/env bash
# run_eval.sh — runs the 01-ingest eval-cases against an input.
# Usage: run_eval.sh <input_id>
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

TXT="outputs/${INPUT_ID}/01_ingest/v1.txt"
META="outputs/${INPUT_ID}/01_ingest/v1.meta.json"

# 1. v1.txt must exist and be non-empty
test -f "$TXT" || { echo "FAIL: $TXT missing"; exit 2; }
size=$(wc -c < "$TXT")
test "$size" -gt 0 || { echo "FAIL: $TXT empty"; exit 2; }

# 2. meta exists
test -f "$META" || { echo "FAIL: $META missing"; exit 2; }

# 3. meta.metadata.fetched_at set
fetched_at=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['metadata']['fetched_at'])")
test -n "$fetched_at" || { echo "FAIL: metadata.fetched_at not set"; exit 2; }

# 4. if 00_research/v1.json existed, research_ref must be set
if [ -f "outputs/${INPUT_ID}/00_research/v1.json" ]; then
    research_ref=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['metadata']['research_ref'])")
    test -n "$research_ref" || { echo "FAIL: 00_research existed but metadata.research_ref not set"; exit 2; }
    # And v1.txt must contain "## Research Context"
    grep -q "## Research Context" "$TXT" || { echo "FAIL: 00_research existed but v1.txt has no Research Context block"; exit 2; }
fi

# 5. trace
uv run python -m tools.trace gate \
    --run-id "run-${INPUT_ID}" \
    --gate 01_ingest_self_check \
    --status pass

echo "OK 01-ingest for ${INPUT_ID}"
