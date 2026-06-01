"""manifest.py — build + read the pipeline-level manifest.json.

The manifest is the audit trail for one input. Required for any pipeline run
to be considered 'done'.

Usage:
    from tools.manifest import init_manifest, record_attempt, finalize
    init_manifest(input_id, input_source="file", input_ref=path, hash_str=..., size=N)
    record_attempt(input_id, "01_ingest", version=1, status="pass", score=0.9)
    finalize(input_id)
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.artifact_io import OUTPUTS, REPO, atomic_write, now_iso


def _load_pipeline() -> dict:
    return json.loads((REPO / "pipeline.json").read_text())


def _stage_ids() -> list[str]:
    return [s["id"] for s in _load_pipeline()["stages"]]


def manifest_path(input_id: str) -> Path:
    return OUTPUTS / input_id / "manifest.json"


def init_manifest(
    input_id: str,
    *,
    input_hash: str,
    input_source: str,
    input_ref: str = "",
    size_bytes: int = 0,
) -> dict:
    """Create a fresh manifest skeleton with one entry per stage."""
    pipeline = _load_pipeline()
    manifest: dict[str, Any] = {
        "input_id": input_id,
        "input_hash": f"sha256:{input_hash}" if not input_hash.startswith("sha256:") else input_hash,
        "input_size_bytes": size_bytes,
        "input_source": input_source,
        "input_ref": input_ref,
        "pipeline_version": pipeline.get("version", "1.0"),
        "started_at": now_iso(),
        "completed_at": "",
        "stages": [
            {
                "id": sid,
                "attempts": [],
                "winner": "",
            }
            for sid in _stage_ids()
        ],
    }
    write_manifest(input_id, manifest)
    return manifest


def read_manifest(input_id: str) -> dict | None:
    p = manifest_path(input_id)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def write_manifest(input_id: str, manifest: dict) -> Path:
    p = manifest_path(input_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(p, json.dumps(manifest, indent=2, ensure_ascii=False))
    return p


def record_attempt(
    input_id: str,
    stage: str,
    version: int,
    status: str,
    *,
    score: float = 0.0,
    options: int | None = None,
    picked: str | None = None,
    feedback: str = "",
) -> None:
    """Append one attempt to a stage's entry. If status='pass', sets that version as winner."""
    manifest = read_manifest(input_id) or {}
    stages = {s["id"]: s for s in manifest.get("stages", [])}
    if stage not in stages:
        stages[stage] = {"id": stage, "attempts": [], "winner": ""}
        manifest.setdefault("stages", []).append(stages[stage])
    entry = stages[stage]
    attempt: dict[str, Any] = {"version": version, "status": status, "score": score}
    if options is not None:
        attempt["options"] = options
    if picked is not None:
        attempt["picked"] = picked
    if feedback:
        attempt["feedback"] = feedback
    entry["attempts"].append(attempt)
    if status == "pass":
        entry["winner"] = f"v{version}"
    write_manifest(input_id, manifest)


def finalize(input_id: str) -> None:
    """Mark the manifest as completed (sets completed_at)."""
    manifest = read_manifest(input_id) or {}
    manifest["completed_at"] = now_iso()
    write_manifest(input_id, manifest)


def is_done(input_id: str) -> bool:
    """All stages have a winner."""
    manifest = read_manifest(input_id)
    if not manifest:
        return False
    return all(s.get("winner") for s in manifest.get("stages", []))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m tools.manifest <read|is-done> <input_id>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "read":
        print(json.dumps(read_manifest(sys.argv[2]), indent=2))
    elif cmd == "is-done":
        print(is_done(sys.argv[2]))
    else:
        print(f"unknown cmd: {cmd}")
        sys.exit(1)
