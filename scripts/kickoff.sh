#!/usr/bin/env bash
# kickoff.sh — wrapper that delegates to kickoff.py
exec python3 "$(dirname "$0")/kickoff.py" "$@"
