"""Compatibility shim for ``research_pipeline.tools.artifact_io``."""
from __future__ import annotations

from ._compat import ensure_src_path, run_module

ensure_src_path()

if __name__ == "__main__":
    run_module("research_pipeline.tools.artifact_io")
else:
    from research_pipeline.tools.artifact_io import *  # noqa: F401,F403,E402
