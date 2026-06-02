#!/usr/bin/env python3
"""status.py — unified dashboard / status check for the research swarm.

Usage:
  python scripts/status.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from research_pipeline.paths import REPO_ROOT

REPO = REPO_ROOT
HCOM_SENDER = "bigboss"

def load_dotenv() -> None:
    env_file = REPO / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip("'\"")
                    os.environ[key.strip()] = val
        except Exception as e:
            print(f"Warning: failed to load .env: {e}", file=sys.stderr)

def get_git_info() -> tuple[str, str]:
    try:
        branch = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
        sha = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        return branch or "detached", sha or "n/a"
    except Exception:
        return "detached", "n/a"

def main() -> None:
    load_dotenv()

    home = Path.home()
    local_bin = str(home / ".local" / "bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}{os.pathsep}{os.environ.get('PATH', '')}"

    hcom_bin = shutil.which("hcom")
    hcom_dir = os.environ.get("HCOM_DIR", str(REPO / ".hcom"))
    os.environ["HCOM_DIR"] = hcom_dir

    print("=== research-pipeline status ===")
    print(f"repo:   {REPO}")
    branch, sha = get_git_info()
    print(f"branch: {branch}")
    print(f"sha:    {sha}")
    print()

    print("--- hcom agents ---")
    if hcom_bin:
        try:
            Path(hcom_dir).mkdir(parents=True, exist_ok=True)
            subprocess.run([hcom_bin, "start", "--as", HCOM_SENDER], capture_output=True, text=True)
            r = subprocess.run(
                [hcom_bin, "list", "--name", HCOM_SENDER, "--json"],
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                print(r.stderr or r.stdout)
            else:
                rows = [json.loads(line) for line in r.stdout.splitlines() if line.strip().startswith("{")]
                agents = [row for row in rows if "_self" not in row]
                active = [a for a in agents if a.get("status") in {"active", "listening"}]
                stale = [a for a in agents if a.get("status") == "inactive"]
                print(f"  active/listening: {len(active)}")
                for agent in active:
                    print(f"    {agent.get('name')}: {agent.get('description')}")
                print(f"  inactive: {len(stale)}")
                for agent in stale[:8]:
                    print(f"    {agent.get('name')}: {agent.get('description')}")
                if len(stale) > 8:
                    print(f"    ... {len(stale) - 8} more inactive")
        except Exception:
            print("  (no agents running, or hcom error)")
    else:
        print("  (no agents running, or hcom not on PATH)")
    print()

    print("--- pipeline.json ---")
    pipeline_file = REPO / "pipeline.json"
    if pipeline_file.exists():
        try:
            cfg = json.loads(pipeline_file.read_text(encoding="utf-8"))
            stages = ",".join(s["id"] for s in cfg.get("stages", []))
            print(f"  stages: {stages}")
        except Exception as e:
            print(f"  (error loading pipeline.json: {e})")
    else:
        print("  (missing)")
    print()

    print("--- inputs/inbox/ ---")
    inbox_dir = REPO / "inputs" / "inbox"
    if inbox_dir.exists():
        pending = sorted([p for p in inbox_dir.iterdir() if p.is_file()])
        print(f"  pending files: {len(pending)}")
        for f in pending:
            print(f"    {f.name}")
    else:
        print("  (no inputs/inbox/ yet)")
    print()

    print("--- outputs/ ---")
    outputs_dir = REPO / "outputs"
    if outputs_dir.exists():
        runs = sorted([d for d in outputs_dir.iterdir() if d.is_dir()])
        print(f"  input runs: {len(runs)}")
        for d in runs:
            manifest_file = d / "manifest.json"
            trace_file = d / "trace.jsonl"
            
            # Read token usage and tool calls from trace.jsonl if present
            total_tokens = 0
            total_tool_calls = 0
            cost_usd = 0.0
            if trace_file.exists():
                try:
                    for line in trace_file.read_text(encoding="utf-8").splitlines():
                        if line.strip():
                            tdata = json.loads(line)
                            total_tokens += tdata.get("tokens_used", 0)
                            total_tool_calls += tdata.get("tool_calls_count", 0)
                    # Generic rate: $5.00 per 1M tokens
                    cost_usd = (total_tokens / 1_000_000) * 5.00
                except Exception:
                    pass
            
            if manifest_file.exists():
                try:
                    m = json.loads(manifest_file.read_text(encoding="utf-8"))
                    stages_list = m.get("stages", [])
                    winners = sum(1 for s in stages_list if s.get("winner"))
                    cost_str = f" | {total_tokens:,} tokens | {total_tool_calls} tools | ~${cost_usd:.4f} USD" if total_tokens else ""
                    print(f"    {d.name}: {winners}/{len(stages_list)} stages done{cost_str}")
                except Exception:
                    print(f"    {d.name}: (error reading manifest)")
            else:
                print(f"    {d.name}: (no manifest)")
    else:
        print("  (no outputs/ yet - run python scripts/run_pipeline.py <input>)")
    print()

    print("--- learnings.md ---")
    learnings_file = REPO / "learnings.md"
    if learnings_file.exists():
        lines = learnings_file.read_text(encoding="utf-8").splitlines()
        print(f"  lines: {len(lines)} (cap 200)")
    else:
        print("  (no learnings.md yet)")
    print()

    print("--- progress.md ---")
    progress_file = REPO / "progress.md"
    if progress_file.exists():
        lines = progress_file.read_text(encoding="utf-8").splitlines()
        print(f"  lines: {len(lines)}")
        if lines:
            print("  last entry:")
            print(f"    {lines[-1]}")
    else:
        print("  (no progress.md yet)")

if __name__ == "__main__":
    main()
