#!/usr/bin/env python3
"""launch.py — Cross-platform Python launcher for the AI agents swarm.

Usage:
  python scripts/launch.py
  python scripts/launch.py --mixed
  python scripts/launch.py 5
  python scripts/launch.py --tag mytag
"""
from __future__ import annotations

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
                    # Strip quotes if present
                    val = val.strip().strip("'\"")
                    os.environ[key.strip()] = val
        except Exception as e:
            print(f"Warning: failed to load .env: {e}", file=sys.stderr)

def main() -> None:
    load_dotenv()

    # Add $HOME/.local/bin to PATH for Unix-like OS
    home = Path.home()
    local_bin = str(home / ".local" / "bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}{os.pathsep}{os.environ.get('PATH', '')}"

    hcom_bin = shutil.which("hcom")
    if not hcom_bin:
        print("hcom not found. Install: brew install aannoo/hcom/hcom, or check github.com/aannoo/hcom", file=sys.stderr)
        sys.exit(1)

    # Setup HCOM_DIR
    hcom_dir = REPO / ".hcom"
    hcom_dir.mkdir(parents=True, exist_ok=True)
    os.environ["HCOM_DIR"] = str(hcom_dir)
    os.environ.setdefault("HCOM_NAME_EXPORT", "HCOM_NAME")

    start = subprocess.run(
        [hcom_bin, "start", "--as", HCOM_SENDER],
        capture_output=True,
        text=True,
    )
    if start.returncode != 0:
        print(f"hcom start failed: {start.stderr or start.stdout}", file=sys.stderr)
        sys.exit(1)

    # Ensure hooks are added
    try:
        r = subprocess.run([hcom_bin, "hooks"], capture_output=True, text=True)
        if r.returncode != 0:
            subprocess.run([hcom_bin, "hooks", "add", "claude"], capture_output=True)
    except Exception:
        pass

    # Parse arguments
    args = sys.argv[1:]
    count = 8
    tag = "research-pipeline"
    tools_claude = 0
    tools_gemini = 0
    tools_codex = 0
    tools_agy = 0

    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg == "--mixed":
            tools_claude = 4
            tools_gemini = 2
            tools_codex = 1
            idx += 1
        elif arg == "--tag":
            if idx + 1 < len(args):
                tag = args[idx + 1]
                idx += 2
            else:
                print("Missing value for --tag", file=sys.stderr)
                sys.exit(1)
        elif arg == "--claude":
            if idx + 1 < len(args):
                tools_claude = int(args[idx + 1])
                idx += 2
            else:
                print("Missing value for --claude", file=sys.stderr)
                sys.exit(1)
        elif arg == "--gemini":
            if idx + 1 < len(args):
                tools_gemini = int(args[idx + 1])
                idx += 2
            else:
                print("Missing value for --gemini", file=sys.stderr)
                sys.exit(1)
        elif arg == "--codex":
            if idx + 1 < len(args):
                tools_codex = int(args[idx + 1])
                idx += 2
            else:
                print("Missing value for --codex", file=sys.stderr)
                sys.exit(1)
        elif arg.isdigit():
            count = int(arg)
            idx += 1
        else:
            print(f"unknown arg: {arg}", file=sys.stderr)
            sys.exit(1)

    if (tools_claude + tools_gemini + tools_codex + tools_agy) == 0:
        tools_claude = count

    # We will spawn the agents individually with sequential tags so that their prefix names
    # (e.g. research-pipeline-claude-1-zulu) match the targets (e.g. @research-pipeline-claude-1)
    print(f"-> Launching {count} agents sequentially...")
    print(f"-> HCOM_DIR={hcom_dir}")
    print("-> When agents are ready, run: python scripts/kickoff.py (or ./scripts/kickoff.sh)")
    print()

    try:
        for i in range(1, count + 1):
            agent_tag = f"{tag}-claude-{i}"
            env = os.environ.copy()
            env["HCOM_TAG"] = agent_tag
            env["HCOM_NAME_EXPORT"] = "HCOM_NAME"
            
            spawn_cmd = [hcom_bin, "1", "claude"]
            print(f"-> Launching Agent {i}/{count} with tag: {agent_tag}")
            
            if sys.platform != "win32":
                # On Unix, run in background (detach)
                subprocess.Popen(spawn_cmd, env=env, start_new_session=True)
            else:
                # On Windows, run subprocess directly (hcom handles terminal creation asynchronously)
                subprocess.run(spawn_cmd, env=env)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
