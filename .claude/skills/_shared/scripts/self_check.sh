#!/usr/bin/env bash
# self_check.sh — run a v1.json through the skill's self_check list.
#
# Usage: self_check.sh <skill-stage-id> <input_id> [<version>]
set -euo pipefail
SKILL="${1:?usage: $0 <skill> <input_id> [<version>]}"
INPUT_ID="${2:?usage: $0 <skill> <input_id> [<version>]}"
VERSION="${3:-1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

ARTIFACT="outputs/${INPUT_ID}/${SKILL}/v${VERSION}.json"
META="${ARTIFACT%.json}.meta.json"

test -f "$ARTIFACT" || { echo "FAIL: artifact missing: $ARTIFACT"; exit 2; }
test -f "$META"    || { echo "FAIL: meta missing: $META"; exit 2; }

# 1. meta.producer set
producer=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['producer'])" 2>/dev/null || echo "")
test -n "$producer" || { echo "FAIL: meta.producer not set"; exit 2; }

# 2. meta.validation.status == "pending"
status=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['validation']['status'])")
test "$status" = "pending" || { echo "FAIL: validation.status=$status, expected pending"; exit 2; }

# 3. parent_ref set if not stage 00
if [ "$SKILL" != "00_research" ]; then
    parent=$(uv run python -c "import json; print(json.load(open('$META', encoding='utf-8'))['parent_ref'])" 2>/dev/null || echo "")
    test -n "$parent" || { echo "FAIL: parent_ref not set"; exit 2; }
fi

echo "OK self_check ${SKILL} v${VERSION} for ${INPUT_ID}"
