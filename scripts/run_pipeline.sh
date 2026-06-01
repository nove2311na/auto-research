#!/usr/bin/env bash
# Usage: run_pipeline.sh [--depth shallow|medium|deep] <input_ref>
# run_pipeline.sh — kick off one input through the research pipeline.
#
# Usage:
#   ./scripts/run_pipeline.sh inputs/inbox/note.txt
#   ./scripts/run_pipeline.sh --depth deep inputs/inbox/note.txt
#   ./scripts/run_pipeline.sh https://example.com/article
#   echo "raw text" | ./scripts/run_pipeline.sh -        # from stdin → temp file
#
# What it does:
#   1. Computes input_id (sha256[:8] of the fetched text).
#   2. Creates outputs/<input_id>/.
#   3. Inits a manifest.json skeleton.
#   4. Sends an hcom message to @research-pipeline-claude-1 with the input ref.
#
# The orchestrator takes over from there.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

export PATH="$HOME/.local/bin:$PATH"
export HCOM_DIR="${HCOM_DIR:-$REPO/.hcom}"

# Pre-flight
command -v hcom >/dev/null || { echo "hcom not found" >&2; exit 1; }
[ -d "$HCOM_DIR" ] || { echo "HCOM_DIR not found: $HCOM_DIR. Run ./scripts/launch.sh first." >&2; exit 1; }

if [ $# -lt 1 ]; then
  echo "Usage: $0 [--depth shallow|medium|deep] <path-or-url> [-]" >&2
  exit 1
fi

DEPTH="medium"
INPUT_REF=""
TMPFILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --depth)
      DEPTH="$2"
      shift 2
      ;;
    --depth=*)
      DEPTH="${1#*=}"
      shift
      ;;
    -*)
      echo "Unknown flag: $1" >&2
      exit 1
      ;;
    *)
      INPUT_REF="$1"
      shift
      ;;
  esac
done

# Validate depth
case "$DEPTH" in
  shallow|medium|deep) ;;
  *) echo "Invalid --depth: $DEPTH (must be shallow|medium|deep)" >&2; exit 1 ;;
esac

INPUT="$INPUT_REF"
if [ "$INPUT" = "-" ]; then
  TMPFILE="$(mktemp -t run_pipeline_XXXXXX.txt)"
  cat > "$TMPFILE"
  INPUT="$TMPFILE"
fi

# Compute input_id by fetching the source first.
INPUT_ID=$(uv run python -c "
from tools.fetch_input import fetch, input_id_for
text, meta = fetch('$INPUT')
print(input_id_for(text))
")

if [ -z "$INPUT_ID" ]; then
  echo "failed to compute input_id" >&2
  exit 1
fi

echo "→ input_id: $INPUT_ID"
echo "→ source:   $INPUT"

# Create outputs/<id>/ if missing, init manifest.
uv run python -c "
from pathlib import Path
from tools.fetch_input import fetch
from tools.manifest import init_manifest
text, meta = fetch('$INPUT')
out = Path('outputs') / '$INPUT_ID'
out.mkdir(parents=True, exist_ok=True)
size = meta.get('size_bytes', 0)
src = meta.get('source_type', 'text')
ref = meta.get('source_ref', '$INPUT')
init_manifest('$INPUT_ID', input_hash='$INPUT_ID', input_source=src, input_ref=ref, size_bytes=size)
print(f'→ manifest initialized at {out}/manifest.json')
"

# Send to orchestrator
TARGET="${TARGET:-@research-pipeline-claude-1}"
hcom send "$TARGET" -- \
  --title "process: $INPUT_ID" \
  --description "New input ready. input_id=$INPUT_ID. source=$INPUT. Depth=$DEPTH. Drive it through all 6 stages. Read pipeline.json for the stage list. Initialize prd.json.current_input_id. On completion, call tools.manifest.finalize($INPUT_ID) and move the source to inputs/processed/." \
  --files "$INPUT"

echo "→ Pipeline kicked off for $INPUT_ID"
echo "→ Watch: HCOM_DIR=\"$HCOM_DIR\" hcom"

[ -n "$TMPFILE" ] && rm -f "$TMPFILE"
