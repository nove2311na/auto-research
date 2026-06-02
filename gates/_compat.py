"""Compatibility helpers for the historical root-level gates package."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"


def ensure_src_path() -> None:
    src = str(SRC)
    if src not in sys.path:
        sys.path.insert(0, src)

