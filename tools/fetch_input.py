"""Compatibility shim for ``research_pipeline.tools.fetch_input``."""
from __future__ import annotations

from ._compat import ensure_src_path, run_module

ensure_src_path()

if __name__ == "__main__":
    run_module("research_pipeline.tools.fetch_input")
else:
    from research_pipeline.tools.fetch_input import *  # noqa: F401,F403,E402
