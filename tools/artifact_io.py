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
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUTPUTS = REPO / "outputs"


def stage_dir(input_id: str, stage: str, option: str | None = None) -> Path:
    """Return the directory for a stage. If option is given, append options/<X>/."""
    base = OUTPUTS / input_id / stage
    if option:
        return base / "options" / option
    return base


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def next_version(input_id: str, stage: str, option: str | None = None) -> int:
    """Return the next version number (1, 2, 3, ...) for this stage+option."""
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
    """Return sorted list of existing versions for this stage+option."""
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
    """Write data to path atomically: write to .tmp, fsync, rename."""
    ensure_dir(path.parent)
    mode = "wb" if isinstance(data, bytes) else "w"
    with tempfile.NamedTemporaryFile(
        mode=mode, dir=str(path.parent), prefix=".tmp_", delete=False
    ) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    tmp_path.rename(path)


def write_artifact(
    input_id: str,
    stage: str,
    version: int,
    content: str,
    ext: str = "txt",
    option: str | None = None,
    producer: str = "",
) -> Path:
    """Write a versioned artifact. Returns the path written."""
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
    """Read a versioned artifact. Raises FileNotFoundError if missing."""
    path = stage_dir(input_id, stage, option) / f"v{version}.{ext}"
    return path.read_text()


def artifact_exists(
    input_id: str,
    stage: str,
    version: int,
    ext: str = "txt",
    option: str | None = None,
) -> bool:
    path = stage_dir(input_id, stage, option) / f"v{version}.{ext}"
    return path.exists()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_meta(
    stage: str,
    input_id: str,
    version: int,
    producer: str,
    parent_ref: str = "",
    schema_version: str = "1.0",
) -> dict:
    """Build an empty meta with validation=pending. Critic fills it in later."""
    return {
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


def write_meta(input_id: str, stage: str, version: int, meta: dict, option: str | None = None) -> Path:
    d = ensure_dir(stage_dir(input_id, stage, option))
    path = d / f"v{version}.meta.json"
    atomic_write(path, json.dumps(meta, indent=2, ensure_ascii=False))
    return path


def read_meta(input_id: str, stage: str, version: int, option: str | None = None) -> dict | None:
    path = stage_dir(input_id, stage, option) / f"v{version}.meta.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def pick_winner(
    input_id: str,
    stage: str,
    option_scores: dict[str, float],
    ext: str = "json",
) -> tuple[str, int]:
    """Given a dict {option_letter: score}, copy the highest-scoring option's
    v1.<ext> to the stage root as v1.<ext> and return (winning_letter, new_version).

    The stage root's v1 represents the canonical artifact for downstream stages.
    Side effect: writes the winner's content + meta to <stage>/v1.<ext>.
    """
    if not option_scores:
        raise ValueError("option_scores is empty")
    winner = max(option_scores, key=option_scores.get)
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
