"""Compatibility shim for ``research_pipeline.gates.security_gates``."""
from __future__ import annotations

from ._compat import ensure_src_path

ensure_src_path()

from research_pipeline.gates.security_gates import *  # noqa: F401,F403,E402

