#!/usr/bin/env python3
"""run_pipeline.py — Cross-platform Python pipeline trigger.

Usage:
  python scripts/run_pipeline.py [--depth shallow|medium|deep] <path-or-url>
  echo "raw text" | python scripts/run_pipeline.py -
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from research_pipeline.paths import REPO_ROOT
from research_pipeline.tools.fetch_input import fetch, input_id_for
from research_pipeline.tools.manifest import init_manifest

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

    # PATH adjustment
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

    if not Path(hcom_dir).exists():
        print(f"HCOM_DIR not found: {hcom_dir}. Run python scripts/launch.py first.", file=sys.stderr)
        sys.exit(1)

    start = subprocess.run(
        [hcom_bin, "start", "--as", HCOM_SENDER],
        capture_output=True,
        text=True,
    )
    if start.returncode != 0:
        print(f"hcom start failed: {start.stderr or start.stdout}", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Kick off one input through the research pipeline.")
    parser.add_argument("--depth", choices=["shallow", "medium", "deep"], default="medium", help="Research depth")
    parser.add_argument("input_ref", help="Input file path, URL, or '-' for stdin")

    args = parser.parse_args()

    input_ref = args.input_ref
    temp_file_path = None

    if input_ref == "-":
        content = sys.stdin.read()
        fd, temp_file_path = tempfile.mkstemp(suffix=".txt", prefix="run_pipeline_")
        os.close(fd)
        Path(temp_file_path).write_text(content, encoding="utf-8")
        input_ref = temp_file_path

    try:
        try:
            text, meta = fetch(input_ref)
        except Exception as e:
            print(f"Failed to fetch input '{input_ref}': {e}", file=sys.stderr)
            sys.exit(1)

        input_id = input_id_for(text)
        if not input_id:
            print("Failed to compute input_id", file=sys.stderr)
            sys.exit(1)

        print(f"-> input_id: {input_id}")
        print(f"-> source:   {args.input_ref}")

        out_dir = REPO / "outputs" / input_id
        out_dir.mkdir(parents=True, exist_ok=True)

        size = meta.get("size_bytes", 0)
        src = meta.get("source_type", "text")
        ref = meta.get("source_ref", input_ref)

        init_manifest(input_id, input_hash=input_id, input_source=src, input_ref=ref, size_bytes=size)
        print(f"-> manifest initialized at {out_dir}/manifest.json")

        # Initialize task_plan.md on disk for Planning with Files pattern
        plan_content = f"""# Task Plan: Research for {input_id}

## Goal
Conduct a thorough automated research pipeline execution for input_id={input_id}.

## Phases
- [ ] Phase 1: Ingest and research (00_research & 01_ingest)
- [ ] Phase 2: Extract data facts (02_extract)
- [ ] Phase 3: Analyze themes and gaps (03_analyze)
- [ ] Phase 4: Synthesize positions & hypotheses (04_synthesize)
- [ ] Phase 5: Format final report & review (05_format)

## Key Questions
1. What are the key entities, facts, and themes discovered in the input?
2. What are the main contradictions or gaps identified?

## Decisions Made
- [Setup]: Created task_plan.md to track execution on disk.

## Errors Encountered

## Status
**Currently in Phase 1** - Preparing to kick off research and ingestion.
"""
        plan_file = out_dir / "task_plan.md"
        plan_file.write_text(plan_content, encoding="utf-8")
        print(f"-> task plan initialized at {plan_file}")

        target = os.environ.get("TARGET", "@research-pipeline-claude-1")
        desc = (
            f"New input ready. input_id={input_id}. source={input_ref}. Depth={args.depth}. "
            f"Drive it through all 6 stages. Read pipeline.json for the stage list. "
            f"Initialize prd.json.current_input_id. On completion, call tools.manifest.finalize({input_id}) "
            f"and move the source to inputs/processed/."
        )

        message_text = (
            f"{target} orch: {input_id}\n\n"
            f"depth={escape_hcom_body(args.depth)}\n"
            f"source={escape_hcom_body(input_ref)}\n"
            f"manifest={out_dir / 'manifest.json'}\n"
            f"task_plan={plan_file}\n\n"
            f"{escape_hcom_body(desc)}"
        )

        send_cmd = [hcom_bin, "send", "--name", HCOM_SENDER, "--stdin"]

        r = subprocess.run(send_cmd, input=message_text, capture_output=True, text=True)
        if r.returncode != 0 and WINDOWS_POST_SEND_ERROR not in f"{r.stderr}\n{r.stdout}":
            print(f"hcom send failed: {r.stderr}", file=sys.stderr)
            sys.exit(1)

        print(f"-> Pipeline kicked off for {input_id}")
        print(f"-> Watch: HCOM_DIR=\"{hcom_dir}\" hcom")

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

if __name__ == "__main__":
    main()
