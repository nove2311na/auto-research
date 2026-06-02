#!/usr/bin/env bash
# run_eval.sh — runs the 06-validate eval-cases against an input + stage.
# Usage: run_eval.sh <input_id> <stage> [<version>]
set -euo pipefail
INPUT_ID="${1:?usage: $0 <input_id> <stage>}"
STAGE="${2:?usage: $0 <input_id> <stage>}"
VERSION="${3:-1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

ART="outputs/${INPUT_ID}/${STAGE}/v${VERSION}.json"
META="${ART%.json}.meta.json"

# 1. artifact + meta exist
test -f "$ART"  || { echo "FAIL: $ART missing"; exit 2; }
test -f "$META" || { echo "FAIL: $META missing"; exit 2; }

# 2. validation block has all 5 required fields
for f in status validator validated_at score feedback; do
    v=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['validation'].get('$f', ''))")
    test -n "$v" || { echo "FAIL: validation.$f empty"; exit 2; }
done

# 3. status is pass or fail
status=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['validation']['status'])")
test "$status" = "pass" -o "$status" = "fail" || { echo "FAIL: validation.status=$status"; exit 2; }

# 4. checks block has all 3 keys
for c in schema completeness llm_judge; do
    v=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['validation']['checks'].get('$c', ''))")
    test -n "$v" || { echo "FAIL: validation.checks.$c empty"; exit 2; }
done

# 5. score in [0.0, 1.0]
score=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['validation']['score'])")
uv run python -c "assert 0.0 <= $score <= 1.0, 'score out of range'" || { echo "FAIL: score=$score out of [0,1]"; exit 2; }

# 6. if pass, score must be >= pipeline.json#critic.llm_judge_threshold; if fail, must have feedback
if [ "$status" = "pass" ]; then
    threshold=$(uv run python -c "import json; print(json.load(open('pipeline.json', encoding='utf-8'))['critic']['llm_judge_threshold'])")
    uv run python -c "assert $score >= $threshold, f'pass with score $score < threshold $threshold'" || { echo "FAIL: pass with score < threshold"; exit 2; }
fi

# 7. trace
uv run python -m tools.trace gate --run-id "run-${INPUT_ID}" --gate "${STAGE}_validation" --status "$status"

echo "OK 06-validate for ${INPUT_ID} ${STAGE} v${VERSION} status=$status"
