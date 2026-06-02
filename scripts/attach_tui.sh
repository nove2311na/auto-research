#!/usr/bin/env bash
# attach_tui.sh — wrapper that delegates to attach_tui.py
exec python3 "$(dirname "$0")/attach_tui.py" "$@"
