"""Compatibility shim for ``research_pipeline.tools.observability.render_dashboard``."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
src_str = str(SRC)
if src_str not in sys.path:
    sys.path.insert(0, src_str)

import runpy

if __name__ == "__main__":
    runpy.run_module("research_pipeline.tools.observability.render_dashboard", run_name="__main__")
else:
    from research_pipeline.tools.observability.render_dashboard import *  # noqa: F401,F403,E402
