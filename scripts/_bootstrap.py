"""Bootstrap helpers for root-level compatibility scripts."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"


def run_module(module_name: str) -> None:
    """Run a module from the src-layout package as __main__."""
    src = str(SRC)
    if src not in sys.path:
        sys.path.insert(0, src)
    runpy.run_module(module_name, run_name="__main__")

