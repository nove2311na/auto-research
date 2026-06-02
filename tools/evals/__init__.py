"""Compatibility package for historical ``tools.evals`` imports."""
from __future__ import annotations

from tools._compat import ensure_src_path

ensure_src_path()

from research_pipeline.tools.evals import *  # noqa: F401,F403,E402

