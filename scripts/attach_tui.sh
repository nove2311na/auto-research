#!/usr/bin/env bash
# attach_tui.sh — open the hcom TUI dashboard.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
export HCOM_DIR="$REPO/.hcom"
exec hcom
