#!/usr/bin/env bash
# batch_run.sh — wrapper that delegates to batch_run.py
exec python3 "$(dirname "$0")/batch_run.py" "$@"
