#!/usr/bin/env bash
# run_eval.sh — runs the 04-synthesize eval-cases against an input.
# Usage: run_eval.sh <input_id>
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

ART="outputs/${INPUT_ID}/04_synthesize/v1.json"

# 1. schema check
uv run python -m gates.output_gates json_schema --artifact "$ART" --schema schemas/04_synthesize.json

# 2. summary non-empty
summary=$(uv run python -c "import json; print(json.load(open('$ART', encoding='utf-8'))['summary'])")
test -n "$summary" || { echo "FAIL: summary empty"; exit 2; }

# 3. insights 3-7
n=$(uv run python -c "import json; print(len(json.load(open('$ART', encoding='utf-8'))['insights']))")
test "$n" -ge 3 && test "$n" -le 7 || { echo "FAIL: insights=$n, expected 3-7"; exit 2; }

# 4. diagrams >= 2, with at least 1 flowchart and 1 mindmap
n=$(uv run python -c "import json; print(len(json.load(open('$ART', encoding='utf-8'))['diagrams']))")
test "$n" -ge 2 || { echo "FAIL: diagrams=$n, expected >=2"; exit 2; }
has_fc=$(uv run python -c "import json; d=json.load(open('$ART', encoding='utf-8')); print(any(x['type']=='flowchart' for x in d['diagrams']))")
has_mm=$(uv run python -c "import json; d=json.load(open('$ART', encoding='utf-8')); print(any(x['type']=='mindmap' for x in d['diagrams']))")
test "$has_fc" = "True" || { echo "FAIL: no flowchart in diagrams"; exit 2; }
test "$has_mm" = "True" || { echo "FAIL: no mindmap in diagrams"; exit 2; }

# 5. theses >= 2
n=$(uv run python -c "import json; print(len(json.load(open('$ART', encoding='utf-8'))['theses']))")
test "$n" -ge 2 || { echo "FAIL: theses=$n, expected >=2"; exit 2; }

# 6. trace
uv run python -m tools.trace gate --run-id "run-${INPUT_ID}" --gate 04_synthesize_self_check --status pass

echo "OK 04-synthesize for ${INPUT_ID}"
