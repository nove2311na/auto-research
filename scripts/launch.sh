#!/usr/bin/env bash
# launch.sh — wrapper that delegates to launch.py
exec python3 "$(dirname "$0")/launch.py" "$@"
