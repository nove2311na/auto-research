"""Release gates before pushing changes to production/main."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.paths import OUTPUTS


def _ok(summary: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": "pass", "summary": summary, "evidence": evidence or [], "risks": []}


def _fail(summary: str, evidence: list[str], risks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": "fail", "summary": summary, "evidence": evidence, "risks": risks}


def release_gate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate release parameters:

    1. Check all 6 stages have winner set.
    2. Check completed_at is set and non-empty.
    3. Check outputs/<input_id>/05_format/v1.md exists and is non-empty.
    """
    input_id = input_data.get("input_id", "")
    manifest = input_data.get("manifest", {})

    evidence = [f"input_data: {input_data}"]

    # Try to load manifest from disk if not provided but input_id is available
    if not manifest and input_id:
        manifest_path = OUTPUTS / input_id / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                evidence.append(f"Loaded manifest from {manifest_path}")
            except Exception as e:
                return _fail(
                    f"Failed to read manifest file: {e}",
                    evidence + [str(manifest_path)],
                    [{"severity": "high", "description": "unreadable manifest.json", "required_fix": "fix manifest file"}],
                )

    if not manifest:
        return _fail(
            "Manifest not found or not provided.",
            evidence,
            [{"severity": "high", "description": "missing manifest", "required_fix": "provide or create manifest"}],
        )

    # 1. Check all 6 stages have winner set
    expected_stages = ["00_research", "01_ingest", "02_extract", "03_analyze", "04_synthesize", "05_format"]
    manifest_stages = manifest.get("stages", [])
    stages_by_id = {s.get("id"): s for s in manifest_stages if s.get("id")}

    for stage_id in expected_stages:
        if stage_id not in stages_by_id:
            return _fail(
                f"Stage '{stage_id}' is missing from the manifest.",
                evidence + [str(manifest)],
                [{"severity": "high", "description": f"missing stage {stage_id} in manifest", "required_fix": "re-run pipeline"}],
            )
        winner = stages_by_id[stage_id].get("winner", "")
        if not winner:
            return _fail(
                f"Stage '{stage_id}' has no winner set in the manifest.",
                evidence + [str(manifest)],
                [{"severity": "high", "description": f"missing winner for stage {stage_id}", "required_fix": "validate stage successfully"}],
            )

    # 2. Check completed_at is set and non-empty
    completed_at = manifest.get("completed_at", "")
    if not completed_at:
        return _fail(
            "Manifest completed_at timestamp is missing or empty.",
            evidence + [str(manifest)],
            [{"severity": "high", "description": "pipeline run not finalized", "required_fix": "finalize the manifest"}],
        )

    # 3. Check outputs/<input_id>/05_format/v1.md exists and is non-empty
    if input_id:
        v1_md_path = OUTPUTS / input_id / "05_format" / "v1.md"
        if not v1_md_path.exists():
            return _fail(
                f"Formatter markdown report not found: {v1_md_path}",
                evidence + [str(v1_md_path)],
                [{"severity": "high", "description": "missing final markdown report", "required_fix": "run formatter stage"}],
            )
        content = v1_md_path.read_text(encoding="utf-8").strip()
        if not content:
            return _fail(
                f"Formatter markdown report is empty: {v1_md_path}",
                evidence + [str(v1_md_path)],
                [{"severity": "high", "description": "empty final markdown report", "required_fix": "regenerate report"}],
            )
    else:
        return _fail(
            "Missing input_id parameter required to verify markdown report presence.",
            evidence,
            [{"severity": "medium", "description": "missing input_id", "required_fix": "provide input_id"}],
        )

    return _ok("release gate passed", evidence)
