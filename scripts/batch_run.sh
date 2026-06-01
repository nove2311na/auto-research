#!/usr/bin/env bash
# batch_run.sh — process every file currently in inputs/inbox/.
#
# Usage:
#   ./scripts/batch_run.sh                # all files
#   ./scripts/batch_run.sh --dry-run      # show what would be processed
#
# Loops over inputs/inbox/* and calls run_pipeline.sh on each.
# Idempotent: re-running skips files whose content-hash is already in outputs/.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

export PATH="$HOME/.local/bin:$PATH"
export HCOM_DIR="${HCOM_DIR:-$REPO/.hcom}"

DRY_RUN=0
DEPTH_ARGS=()

# Parse flags; pass positional input paths to the loop.
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --depth)
      DEPTH_ARGS=(--depth "$2")
      shift 2
      ;;
    --depth=*)
      DEPTH_ARGS=(--depth "${1#*=}")
      shift
      ;;
    *)
      echo "Unknown flag: $1" >&2
      exit 1
      ;;
  esac
done

# Validate depth (if provided)
if [[ ${#DEPTH_ARGS[@]} -gt 0 ]]; then
  case "${DEPTH_ARGS[1]}" in
    shallow|medium|deep) ;;
    *) echo "Invalid --depth: ${DEPTH_ARGS[1]} (must be shallow|medium|deep)" >&2; exit 1 ;;
  esac
fi

INBOX="$REPO/inputs/inbox"
if [ ! -d "$INBOX" ]; then
  echo "no inputs/inbox/ directory" >&2
  exit 1
fi

shopt -s nullglob
FILES=("$INBOX"/*)
shopt -u nullglob

if [ ${#FILES[@]} -eq 0 ]; then
  echo "(inputs/inbox/ is empty — nothing to process)"
  exit 0
fi

for f in "${FILES[@]}"; do
  if [ $DRY_RUN -eq 1 ]; then
    echo "would process: $f"
    continue
  fi
  echo "═══ $f ═══"
  ./scripts/run_pipeline.sh "${DEPTH_ARGS[@]}" "$f"
  echo
done

echo "→ all queued. hcom agents will process in order."
