"""Implementation gates between plan and code integration."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from research_pipeline.paths import OUTPUTS


def _ok(summary: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": "pass", "summary": summary, "evidence": evidence or [], "risks": []}


def _fail(summary: str, evidence: list[str], risks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": "fail", "summary": summary, "evidence": evidence, "risks": risks}


def implementation_gate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate the implementation before code integration.

    Checks:
    1. Version format is valid (e.g. "v1", "v2").
    2. The stage directory exists.
    3. If manifest is provided, verifies that parent stage has a winner.
    """
    input_id = input_data.get("input_id", "")
    stage = input_data.get("stage", "")
    version = str(input_data.get("version", ""))
    manifest = input_data.get("manifest", {})

    evidence = [f"input_data: {input_data}"]

    # 1. Version format check
    if version:
        # Match e.g. "v1", "v2", "v12"
        if not re.match(r"^v\d+$", version):
            return _fail(
                f"Invalid version format: '{version}'. Expected format 'v<digits>'.",
                evidence,
                [{"severity": "high", "description": "version format is invalid", "required_fix": "use format vN"}],
            )
    else:
        return _fail(
            "Version not provided.",
            evidence,
            [{"severity": "medium", "description": "missing version field", "required_fix": "provide version parameter"}],
        )

    # 2. Stage directory check
    if input_id and stage:
        stage_dir = OUTPUTS / input_id / stage
        if not stage_dir.exists():
            return _fail(
                f"Stage directory does not exist: {stage_dir}",
                evidence + [str(stage_dir)],
                [{"severity": "high", "description": "missing stage folder", "required_fix": "create stage folder"}],
            )
    else:
        # If input_id or stage is missing, we check if they are expected in input_data
        missing = []
        if not input_id:
            missing.append("input_id")
        if not stage:
            missing.append("stage")
        return _fail(
            f"Missing required parameters for directory check: {', '.join(missing)}",
            evidence,
            [{"severity": "medium", "description": "missing metadata fields", "required_fix": "provide input_id and stage"}],
        )

    # 3. Parent winner check (using manifest if provided)
    if manifest and stage:
        stages_order = ["00_research", "01_ingest", "02_extract", "03_analyze", "04_synthesize", "05_format"]
        if stage in stages_order:
            idx = stages_order.index(stage)
            if idx > 0:
                parent_stage = stages_order[idx - 1]
                # Look up parent stage in manifest
                manifest_stages = manifest.get("stages", [])
                parent_entry = next((s for s in manifest_stages if s.get("id") == parent_stage), None)
                if not parent_entry or not parent_entry.get("winner"):
                    return _fail(
                        f"Parent stage '{parent_stage}' has no winner yet in manifest.",
                        evidence + [str(manifest)],
                        [{"severity": "high", "description": "parent stage winner missing", "required_fix": "run parent stage first"}],
                    )

    return _ok("implementation gate passed", evidence)
