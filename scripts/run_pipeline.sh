#!/usr/bin/env bash
# run_pipeline.sh — wrapper that delegates to run_pipeline.py
exec python3 "$(dirname "$0")/run_pipeline.py" "$@"
