#!/usr/bin/env bash
# status.sh — wrapper that delegates to status.py
exec python3 "$(dirname "$0")/status.py" "$@"
