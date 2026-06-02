#!/usr/bin/env python3
"""batch_run.py — Cross-platform Python batch processing script.

Usage:
  python scripts/batch_run.py [--dry-run] [--depth shallow|medium|deep]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from research_pipeline.paths import REPO_ROOT

REPO = REPO_ROOT

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

def main() -> None:
    load_dotenv()

    home = Path.home()
    local_bin = str(home / ".local" / "bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}{os.pathsep}{os.environ.get('PATH', '')}"

    hcom_dir = os.environ.get("HCOM_DIR", str(REPO / ".hcom"))
    os.environ["HCOM_DIR"] = hcom_dir

    parser = argparse.ArgumentParser(description="Process every file currently in inputs/inbox/.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without running")
    parser.add_argument("--depth", choices=["shallow", "medium", "deep"], default="medium", help="Research depth")

    args = parser.parse_args()

    inbox_dir = REPO / "inputs" / "inbox"
    if not inbox_dir.exists():
        print("no inputs/inbox/ directory", file=sys.stderr)
        sys.exit(1)

    files = sorted([p for p in inbox_dir.iterdir() if p.is_file()])
    if not files:
        print("(inputs/inbox/ is empty - nothing to process)")
        sys.exit(0)

    for f in files:
        if args.dry_run:
            print(f"would process: {f}")
            continue

        print(f"=== {f} ===")
        run_cmd = [sys.executable, str(REPO / "scripts" / "run_pipeline.py"), "--depth", args.depth, str(f)]
        subprocess.run(run_cmd)
        print()

    if not args.dry_run:
        print("-> all queued. hcom agents will process in order.")

if __name__ == "__main__":
    main()
