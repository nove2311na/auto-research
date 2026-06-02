#!/usr/bin/env python3
"""kickoff.py — Cross-platform Python kickoff trigger.

Usage:
  python scripts/kickoff.py
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
WINDOWS_POST_SEND_ERROR = "PTY wrapper requires Unix-only APIs"


def escape_hcom_body(text: str) -> str:
    return text.replace("@", "[at]")

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

    hcom_bin = shutil.which("hcom")
    if not hcom_bin:
        print("hcom not found", file=sys.stderr)
        sys.exit(1)

    hcom_dir = os.environ.get("HCOM_DIR", str(REPO / ".hcom"))
    os.environ["HCOM_DIR"] = hcom_dir
    Path(hcom_dir).mkdir(parents=True, exist_ok=True)

    start = subprocess.run(
        [hcom_bin, "start", "--as", HCOM_SENDER],
        capture_output=True,
        text=True,
    )
    if start.returncode != 0:
        print(f"hcom start failed: {start.stderr or start.stdout}", file=sys.stderr)
        sys.exit(1)

    target = os.environ.get("TARGET", "@research-pipeline-claude-1")

    desc = (
        "You are the orchestrator of a 7-agent content-research pipeline. "
        "Pipeline: 01_ingest -> 02_extract -> 03_analyze -> 04_synthesize -> 05_format, "
        "each followed by a critic validation. Source of truth: pipeline.json. "
        "Read AGENTS.md first, then pipeline.json, then prd.json. "
        "Idle behavior: wait for hcom messages. "
        "When a new input appears in inputs/inbox/, process it through all 5 stages: "
        "send each task via hcom send @<tag>, wait for the stage agent to write its "
        "artifact + meta, then send @critic for validation, then advance. "
        "On validation fail: retry with feedback (v+1) up to max_retries, then halt. "
        "On 05_format pass: call tools.manifest.finalize, move source file to "
        "inputs/processed/, append to progress.md, sit idle. "
        "Never edit artifact content. Never validate yourself. Never pause to ask the human. "
        "Use tools/artifact_io.py + tools/manifest.py + tools/validator.py for all file operations."
    )

    files = ["pipeline.json", "prd.json", "AGENTS.md"]
    found_files = []
    for f in files:
        p = REPO / f
        if p.exists():
            found_files.append(str(p))

    message_text = f"{target} orch: kickoff\n\n{escape_hcom_body(desc)}"
    if found_files:
        message_text += f"\n\nFiles attached:\n" + "\n".join(f"- {f}" for f in found_files)

    send_cmd = [hcom_bin, "send", "--name", HCOM_SENDER, "--stdin"]

    r = subprocess.run(send_cmd, input=message_text, capture_output=True, text=True)
    if r.returncode != 0 and WINDOWS_POST_SEND_ERROR not in f"{r.stderr}\n{r.stdout}":
        print(f"hcom send failed: {r.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"-> Kickoff sent to {target}")
    print("-> Watch with: python scripts/attach_tui.py (or ./scripts/attach_tui.sh)")
    print("-> Drop a file in inputs/inbox/ to start a pipeline run")

if __name__ == "__main__":
    main()
