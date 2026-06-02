"""Input gates that run before the orchestrator accepts an input."""
from __future__ import annotations

import os
from typing import Any


def completeness_gate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate raw user input (e.g. non-empty, path exists, safe file size)."""
    ref = input_data.get("ref", "")
    if not ref:
        return {"status": "fail", "summary": "missing 'ref' parameter", "evidence": [], "risks": []}
    if not os.path.exists(ref):
        return {"status": "fail", "summary": f"input ref not found on disk: {ref}", "evidence": [], "risks": []}
    return {
        "status": "pass",
        "summary": f"input ref verified: {ref}",
        "evidence": [str(input_data)],
        "risks": [],
    }
