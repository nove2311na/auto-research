#!/usr/bin/env bash
# status.sh — quick health check of the research-pipeline workspace + swarm.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

export PATH="$HOME/.local/bin:$PATH"
export HCOM_DIR="${HCOM_DIR:-$REPO/.hcom}"

echo "═══ research-pipeline status ═══"
echo "repo:   $REPO"
echo "branch: $(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'detached')"
echo "sha:    $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo 'n/a')"
echo

echo "── hcom agents ──"
hcom list 2>/dev/null || echo "  (no agents running, or hcom not on PATH)"
echo

echo "── pipeline.json ──"
if [ -f "$REPO/pipeline.json" ]; then
  echo "  stages: $(uv run python -c "import json; print(','.join(s['id'] for s in json.load(open('$REPO/pipeline.json'))['stages']))" 2>/dev/null)"
else
  echo "  (missing)"
fi
echo

echo "── inputs/inbox/ ──"
if [ -d "$REPO/inputs/inbox" ]; then
  n=$(find "$REPO/inputs/inbox" -maxdepth 1 -type f | wc -l | tr -d ' ')
  echo "  pending files: $n"
  if [ "$n" -gt 0 ]; then
    ls -1 "$REPO/inputs/inbox" | sed 's/^/    /'
  fi
else
  echo "  (no inputs/inbox/ yet)"
fi
echo

echo "── outputs/ ──"
if [ -d "$REPO/outputs" ]; then
  count=$(find "$REPO/outputs" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  echo "  input runs: $count"
  if [ "$count" -gt 0 ]; then
    for d in "$REPO/outputs"/*/; do
      id=$(basename "$d")
      if [ -f "$d/manifest.json" ]; then
        stages=$(uv run python -c "import json; m=json.load(open('$d/manifest.json')); winners=sum(1 for s in m.get('stages',[]) if s.get('winner')); print(f'{winners}/{len(m.get(\"stages\",[]))} stages done')" 2>/dev/null)
        echo "    $id: $stages"
      else
        echo "    $id: (no manifest)"
      fi
    done
  fi
else
  echo "  (no outputs/ yet — run ./scripts/run_pipeline.sh <input>)"
fi
echo

echo "── learnings.md ──"
if [ -f "$REPO/learnings.md" ]; then
  echo "  lines: $(wc -l < "$REPO/learnings.md") (cap 200)"
else
  echo "  (no learnings.md yet)"
fi
echo

echo "── progress.md ──"
if [ -f "$REPO/progress.md" ]; then
  echo "  lines: $(wc -l < "$REPO/progress.md")"
  echo "  last entry:"
  tail -1 "$REPO/progress.md" | sed 's/^/    /'
else
  echo "  (no progress.md yet)"
fi
