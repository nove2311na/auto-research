"""Compatibility helpers for the historical root-level tools package."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"


def ensure_src_path() -> None:
    src = str(SRC)
    if src not in sys.path:
        sys.path.insert(0, src)


def run_module(module_name: str) -> None:
    ensure_src_path()
    runpy.run_module(module_name, run_name="__main__")

