#!/usr/bin/env python3
"""attach_tui.py — Cross-platform Python TUI dashboard attacher.

Usage:
  python scripts/attach_tui.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from research_pipeline.paths import REPO_ROOT

REPO = REPO_ROOT

def main() -> None:
    home = Path.home()
    local_bin = str(home / ".local" / "bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}{os.pathsep}{os.environ.get('PATH', '')}"

    hcom_bin = shutil.which("hcom")
    if not hcom_bin:
        print("hcom not found", file=sys.stderr)
        sys.exit(1)

    os.environ["HCOM_DIR"] = str(REPO / ".hcom")

    if sys.platform != "win32":
        try:
            os.execv(hcom_bin, [hcom_bin])
        except OSError as e:
            print(f"Failed to execute hcom: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            subprocess.run([hcom_bin])
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
