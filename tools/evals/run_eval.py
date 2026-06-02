"""Compatibility shim for ``research_pipeline.tools.evals.run_eval``."""
from __future__ import annotations

from tools._compat import ensure_src_path, run_module

ensure_src_path()

if __name__ == "__main__":
    run_module("research_pipeline.tools.evals.run_eval")
else:
    from research_pipeline.tools.evals.run_eval import *  # noqa: F401,F403,E402
