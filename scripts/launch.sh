#!/usr/bin/env bash
# launch.sh — the ONE command to spawn the 7-agent research-pipeline swarm.
#
# Usage:
#   ./scripts/launch.sh                  # default: 7 Claudes, tag=research-pipeline
#   ./scripts/launch.sh --mixed          # 4 Claude + 2 Gemini + 1 Codex
#   ./scripts/launch.sh 5                # custom swarm size, all Claude
#   ./scripts/launch.sh --tag myexp      # custom tag
#
# After launch, send the kickoff message:
#   ./scripts/kickoff.sh
#
# Or attach the TUI:
#   ./scripts/attach_tui.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Ensure uv on PATH
export PATH="$HOME/.local/bin:$PATH"

# Args
COUNT=7
TAG="research-pipeline"
TOOLS_CLAUDE=0
TOOLS_GEMINI=0
TOOLS_CODEX=0
TOOLS_AGY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --mixed)       TOOLS_CLAUDE=4; TOOLS_GEMINI=2; TOOLS_CODEX=1; shift ;;
    --tag)         TAG="$2"; shift 2 ;;
    --claude)      TOOLS_CLAUDE="$2"; shift 2 ;;
    --gemini)      TOOLS_GEMINI="$2"; shift 2 ;;
    --codex)       TOOLS_CODEX="$2"; shift 2 ;;
    [0-9]*)        COUNT="$1"; shift ;;
    *)             echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Default: all Claude, count = COUNT
if [ $((TOOLS_CLAUDE + TOOLS_GEMINI + TOOLS_CODEX + TOOLS_AGY)) -eq 0 ]; then
  TOOLS_CLAUDE=$COUNT
fi

# Pre-flight
command -v hcom >/dev/null || { echo "hcom not found. Install: brew install aannoo/hcom/hcom" >&2; exit 1; }

# Scoped HCOM_DIR for this worktree
export HCOM_DIR="$REPO/.hcom"
mkdir -p "$HCOM_DIR"

# Install hooks (idempotent)
hcom hooks >/dev/null 2>&1 || hcom hooks add claude >/dev/null 2>&1 || true

# Build the spawn command
SPAWN=(hcom)
[ "$TOOLS_CLAUDE" -gt 0 ] && SPAWN+=("$TOOLS_CLAUDE" "claude")
[ "$TOOLS_GEMINI" -gt 0 ] && SPAWN+=("$TOOLS_GEMINI" "gemini")
[ "$TOOLS_CODEX"  -gt 0 ] && SPAWN+=("$TOOLS_CODEX"  "codex")
[ "$TOOLS_AGY"    -gt 0 ] && SPAWN+=("$TOOLS_AGY"    "agy")
SPAWN+=(--tag "$TAG")

echo "→ Launching: ${SPAWN[*]}"
echo "→ HCOM_DIR=$HCOM_DIR"
echo "→ When agents are ready, run: ./scripts/kickoff.sh"
echo ""

exec "${SPAWN[@]}"
