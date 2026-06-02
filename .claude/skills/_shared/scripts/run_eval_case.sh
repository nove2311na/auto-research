#!/usr/bin/env bash
# run_eval_case.sh — run a single eval-case for a skill against an artifact.
#
# Usage: run_eval_case.sh <skill-stage-id> <input_id> [<version>]
#   skill-stage-id: 00_research | 01_ingest | 02_extract | 03_analyze | 04_synthesize | 05_format
#   input_id: the 8-hex
#   version: default 1
set -euo pipefail
SKILL="${1:?usage: $0 <skill> <input_id> [<version>]}"
INPUT_ID="${2:?usage: $0 <skill> <input_id> [<version>]}"
VERSION="${3:-1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

# 1. JSON schema check (gate)
status="pass"
uv run python -m gates.output_gates json_schema \
    --artifact "outputs/${INPUT_ID}/${SKILL}/v${VERSION}.json" \
    --schema    "schemas/${SKILL}.json" || status="fail"

# 2. Self-check (skill-specific, from skill.json)
SKILL_DIR=".claude/skills/${SKILL}"
test -f "${SKILL_DIR}/skill.json" || { echo "no skill.json for ${SKILL}"; exit 2; }

# 3. Trace
uv run python -m tools.trace gate \
    --run-id "run-${INPUT_ID}" \
    --gate json_schema \
    --status "$status" \
    --evidence "outputs/${INPUT_ID}/${SKILL}/v${VERSION}.json"

if [ "$status" = "fail" ]; then
    echo "FAIL: json_schema gate failed for ${SKILL}"
    exit 2
fi

echo "OK ${SKILL} v${VERSION} for ${INPUT_ID}"
