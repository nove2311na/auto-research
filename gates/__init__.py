"""Compatibility package for historical ``gates`` imports."""
from __future__ import annotations

from ._compat import ensure_src_path

ensure_src_path()

from research_pipeline.gates import *  # noqa: F401,F403,E402

