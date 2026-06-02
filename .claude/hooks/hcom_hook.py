"""hcom_hook.py — Cross-platform Python hook wrapper for hcom.

Checks if hcom is available on the system PATH and executes the requested hook command.
Exits silently (0) if hcom is not found, conforming to the fallback logic.
"""
from __future__ import annotations

import shutil
import subprocess
import sys


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(0)
    action = sys.argv[1]

    hcom_path = shutil.which("hcom")
    if not hcom_path:
        # If hcom is not installed, silently succeed (exit 0)
        sys.exit(0)

    try:
        # Run the hcom command and pass through stdout/stderr
        subprocess.run([hcom_path, action], check=False)
    except Exception:
        pass

if __name__ == "__main__":
    main()
