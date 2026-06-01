#!/usr/bin/env bash
# kickoff.sh — send the initial prompt to the orchestrator (claude-1).
#
# Customize the description below for your research strategy. Default targets
# the orchestrator with the standard research-pipeline V1 brief.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

export PATH="$HOME/.local/bin:$PATH"
export HCOM_DIR="${HCOM_DIR:-$REPO/.hcom}"

# Default: target @research-pipeline-claude-1 (the orchestrator)
TARGET="${TARGET:-@research-pipeline-claude-1}"

DESCRIPTION='You are the orchestrator of a 7-agent content-research pipeline. Pipeline: 01_ingest → 02_extract → 03_analyze → 04_synthesize → 05_format, each followed by a critic validation. Source of truth: pipeline.json. Read AGENTS.md first, then pipeline.json, then prd.json. Idle behavior: wait for hcom messages. When a new input appears in inputs/inbox/, process it through all 5 stages: send each task via hcom send @<tag>, wait for the stage agent to write its artifact + meta, then send @critic for validation, then advance. On validation fail: retry with feedback (v+1) up to max_retries, then halt. On 05_format pass: call tools.manifest.finalize, move source file to inputs/processed/, append to progress.md, sit idle. Never edit artifact content. Never validate yourself. Never pause to ask the human. Use tools/artifact_io.py + tools/manifest.py + tools/validator.py for all file operations.'

hcom send "$TARGET" -- \
  --title "research-pipeline kickoff" \
  --description "$DESCRIPTION" \
  --files ./pipeline.json,./prd.json,./AGENTS.md

echo "→ Kickoff sent to $TARGET"
echo "→ Watch with: ./scripts/attach_tui.sh"
echo "→ Drop a file in inputs/inbox/ to start a pipeline run"
