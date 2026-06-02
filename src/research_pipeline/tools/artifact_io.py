"""artifact_io.py — versioned artifact read/write for the research pipeline.

Convention:
  outputs/<input_id>/<NN_stage>/v<N>.<ext>     <- the artifact
  outputs/<input_id>/<NN_stage>/v<N>.meta.json <- producer + critic metadata
  outputs/<input_id>/<NN_stage>/options/<X>/  <- subfolder per option (A/B/C)

Atomic writes: write to a .tmp sibling, fsync, then rename. Never leave half-written
artifacts visible to other agents.

Usage:
    from tools.artifact_io import (
        new_artifact, write_artifact, read_artifact, read_meta,
        list_versions, pick_winner, next_version, write_meta,
    )
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from research_pipeline.paths import OUTPUTS, REPO_ROOT

REPO = REPO_ROOT


def stage_dir(input_id: str, stage: str, option: str | None = None) -> Path:
    """Return the directory path for a given stage and optional sub-option.

    Args:
        input_id: Unique identifier for the input being processed.
        stage: The directory name of the current pipeline stage (e.g. "01_ingest").
        option: Optional branch option character (e.g. "A").

    Returns:
        Path: The absolute path to the directory.
    """
    base = OUTPUTS / input_id / stage
    if option:
        return base / "options" / option
    return base


def ensure_dir(p: Path) -> Path:
    """Ensure that the given directory path exists. Creates it if necessary.

    Args:
        p: Path to ensure.

    Returns:
        Path: The validated path.
    """
    p.mkdir(parents=True, exist_ok=True)
    return p


def next_version(input_id: str, stage: str, option: str | None = None) -> int:
    """Return the next available version number (1, 2, 3, ...) for this stage+option.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage identifier.
        option: Optional branch letter.

    Returns:
        int: The next incremental version number.
    """
    d = stage_dir(input_id, stage, option)
    if not d.exists():
        return 1
    existing = [
        int(p.name.split(".")[0][1:])
        for p in d.iterdir()
        if p.name.startswith("v") and "." in p.name
        and p.name.split(".")[0][1:].isdigit()
    ]
    return max(existing, default=0) + 1


def list_versions(input_id: str, stage: str, option: str | None = None) -> list[int]:
    """Return sorted list of existing version numbers for this stage+option.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage identifier.
        option: Optional branch letter.

    Returns:
        list[int]: Sorted list of integer version numbers.
    """
    d = stage_dir(input_id, stage, option)
    if not d.exists():
        return []
    versions: list[int] = []
    for p in d.iterdir():
        if p.name.startswith("v") and "." in p.name:
            head = p.name.split(".")[0]
            if head[1:].isdigit():
                versions.append(int(head[1:]))
    return sorted(set(versions))


def atomic_write(path: Path, data: str | bytes) -> None:
    """Write data to path atomically using a temporary file, fsync, and rename.

    Args:
        path: Target filepath.
        data: Str or bytes content to be written.
    """
    ensure_dir(path.parent)
    mode = "wb" if isinstance(data, bytes) else "w"
    with tempfile.NamedTemporaryFile(
        mode=mode, dir=str(path.parent), prefix=".tmp_", delete=False
    ) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def write_artifact(
    input_id: str,
    stage: str,
    version: int,
    content: str,
    ext: str = "txt",
    option: str | None = None,
    producer: str = "",
) -> Path:
    """Write a versioned artifact atomically.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage identifier.
        version: Version number.
        content: File body to write.
        ext: File extension.
        option: Optional branch letter.
        producer: Optional name of the producing agent.

    Returns:
        Path: Path to the written file.
    """
    d = ensure_dir(stage_dir(input_id, stage, option))
    path = d / f"v{version}.{ext}"
    atomic_write(path, content)
    return path


def read_artifact(
    input_id: str,
    stage: str,
    version: int,
    ext: str = "txt",
    option: str | None = None,
) -> str:
    """Read a versioned artifact.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage identifier.
        version: Version number to read.
        ext: Expected file extension.
        option: Optional branch letter.

    Returns:
        str: Read string content.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = stage_dir(input_id, stage, option) / f"v{version}.{ext}"
    return path.read_text()


def artifact_exists(
    input_id: str,
    stage: str,
    version: int,
    ext: str = "txt",
    option: str | None = None,
) -> bool:
    """Check if a versioned artifact exists on disk.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage identifier.
        version: Version number.
        ext: File extension.
        option: Optional branch letter.

    Returns:
        bool: True if exists, else False.
    """
    path = stage_dir(input_id, stage, option) / f"v{version}.{ext}"
    return path.exists()


def now_iso() -> str:
    """Return current UTC time formatted as an ISO-8601 string.

    Returns:
        str: Date-time string.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_meta(
    stage: str,
    input_id: str,
    version: int,
    producer: str,
    parent_ref: str = "",
    schema_version: str = "1.0",
    self_rebuttal_passed: bool | None = None,
    self_rebuttal_notes: str | None = None,
) -> dict[str, Any]:
    """Build a default metadata structure with validation status set to pending.

    Args:
        stage: Pipeline stage name.
        input_id: Unique identifier for the input.
        version: Version number of the artifact.
        producer: Identifier of the agent that produced the artifact.
        parent_ref: Reference to the parent artifact or input.
        schema_version: Metadata schema version string.
        self_rebuttal_passed: Whether the agent passed its internal self-rebuttal.
        self_rebuttal_notes: Notes or rationale from the self-rebuttal review.

    Returns:
        dict[str, Any]: Built metadata dictionary.
    """
    res = {
        "version": version,
        "stage": stage,
        "input_id": input_id,
        "producer": producer,
        "produced_at": now_iso(),
        "parent_ref": parent_ref,
        "schema_version": schema_version,
        "validation": {
            "status": "pending",
            "validator": "",
            "validated_at": "",
            "score": 0.0,
            "feedback": "",
            "checks": {},
        },
    }
    if self_rebuttal_passed is not None:
        res["self_rebuttal_passed"] = self_rebuttal_passed
    if self_rebuttal_notes is not None:
        res["self_rebuttal_notes"] = self_rebuttal_notes
    return res


def write_meta(
    input_id: str,
    stage: str,
    version: int,
    meta: dict[str, Any],
    option: str | None = None,
) -> Path:
    """Write the metadata dictionary associated with a versioned artifact.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage name.
        version: Version number.
        meta: The metadata structure to write.
        option: Optional branch letter.

    Returns:
        Path: Path to the written meta file.
    """
    d = ensure_dir(stage_dir(input_id, stage, option))
    path = d / f"v{version}.meta.json"
    atomic_write(path, json.dumps(meta, indent=2, ensure_ascii=False))
    return path


def read_meta(input_id: str, stage: str, version: int, option: str | None = None) -> dict[str, Any] | None:
    """Read the metadata associated with a versioned artifact.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage name.
        version: Version number.
        option: Optional branch letter.

    Returns:
        dict[str, Any] | None: Loaded metadata dict or None if missing.
    """
    path = stage_dir(input_id, stage, option) / f"v{version}.meta.json"
    if not path.exists():
        return None
    return cast(dict[str, Any], json.loads(path.read_text()))


def pick_winner(
    input_id: str,
    stage: str,
    option_scores: dict[str, float],
    ext: str = "json",
) -> tuple[str, int]:
    """Promote the winning option to the stage root v1 file.

    Given a dict of options to their scores, copies the highest-scoring option's
    v1 to the stage root as the canonical artifact.

    Args:
        input_id: Unique identifier for the input.
        stage: Pipeline stage name.
        option_scores: Map from option identifier to float score.
        ext: Expected file extension of the artifact.

    Returns:
        tuple[str, int]: The winning option key and its promoted version (1).

    Raises:
        ValueError: If option_scores is empty.
        FileNotFoundError: If the winning option does not possess a v1.
    """
    if not option_scores:
        raise ValueError("option_scores is empty")
    winner = max(option_scores, key=lambda k: option_scores[k])
    src_dir = stage_dir(input_id, stage, winner)
    src_path = src_dir / f"v1.{ext}"
    if not src_path.exists():
        raise FileNotFoundError(f"winner option has no v1.{ext}: {src_path}")
    # Copy content to stage root
    dst_dir = ensure_dir(stage_dir(input_id, stage))
    dst_path = dst_dir / f"v1.{ext}"
    shutil.copy2(src_path, dst_path)
    # Copy + amend meta
    src_meta = src_dir / "v1.meta.json"
    if src_meta.exists():
        meta = json.loads(src_meta.read_text())
        meta["picked_option"] = winner
        meta["picked_score"] = option_scores[winner]
    else:
        meta = {"picked_option": winner, "picked_score": option_scores[winner]}
    (dst_dir / "v1.meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return winner, 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m tools.artifact_io <new-version|list|read> <input_id> <stage> [option]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "new-version":
        print(next_version(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
    elif cmd == "list":
        print(list_versions(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
    elif cmd == "read":
        v = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        ext = sys.argv[6] if len(sys.argv) > 6 else "txt"
        opt = sys.argv[7] if len(sys.argv) > 7 else None
        print(read_artifact(sys.argv[2], sys.argv[3], v, ext, opt))
    else:
        print(f"unknown cmd: {cmd}")
        sys.exit(1)
