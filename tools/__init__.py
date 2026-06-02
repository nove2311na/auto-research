"""Compatibility package for historical ``tools`` imports."""
from __future__ import annotations

from ._compat import ensure_src_path

ensure_src_path()

from research_pipeline.tools import *  # noqa: F401,F403,E402
from research_pipeline.tools import spec_io  # noqa: F401,E402

