"""PostToolUse hook — append-only progress.md writer for pipeline stage writes.

Implements the audit-trail step from .claude/agents/orchestrator.json (writes_during_session: prd.json, progress.md) + AGENTS.md § Orchestrator:
  - Read JSON payload from stdin (tool_name, tool_input)
  - If the target is outputs/<id>/<stage>/v<N>.meta.json:
      * Distinguish producer write (validation: pending) vs critic write (pass|fail)
      * Append a progress.md line in the canonical format
  - If the target is outputs/<id>/<stage>/v<N>.<ext> (content write):
      * Assert sibling meta exists; warn if missing
  - Always exit 0; emit {"continue": true}

Conventions (per .claude/rules/python.md):
  - Type hints, pathlib, logging (not print)
  - Standard lib, then third-party, then local
"""
from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

logger = logging.getLogger("claude.hooks.posttooluse")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

META_RE = re.compile(r"^outputs/([^/]+)/(\d{2}_[a-z]+)/v(\d+)\.meta\.json$")
CONTENT_RE = re.compile(r"^outputs/([^/]+)/(\d{2}_[a-z]+)/v(\d+)\.(json|txt|md)$")
PROGRESS_PATH = REPO / "progress.md"

PROGRESS_TEMPLATE = "## {ts} | {input_id} | {event}\n- stage: {stage}\n- attempt: v{ver}\n- status: {status}\n- score: {score}\n- feedback: {feedback}\n"


def _now() -> str:
    """ISO-8601 UTC timestamp (matches tools.artifact_io.now_iso)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_progress(line: str) -> None:
    """Append a single line block to progress.md (idempotent, atomic-ish)."""
    try:
        PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with PROGRESS_PATH.open("a", encoding="utf-8") as f:
            f.write(line if line.endswith("\n") else line + "\n")
    except OSError as exc:
        logger.warning("could not append to progress.md: %s", exc)


def _read_meta_block(file_path: Path) -> dict[str, Any] | None:
    """Read the meta.json sibling of a content write; return the validation block or None."""
    meta_path = file_path.with_suffix(file_path.suffix + ".meta.json")
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _handle_meta_write(file_path: Path, input_id: str, stage: str, ver: int) -> None:
    """Append a progress.md entry for a meta write (producer or critic)."""
    try:
        meta = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("meta file %s is not valid JSON; skipping", file_path)
        return

    validation = meta.get("validation") or {}
    status = validation.get("status", "pending")
    score = validation.get("score", 0.0)
    feedback = validation.get("feedback", "")

    if status == "pending":
        event = "producer-write"
    elif status in ("pass", "fail"):
        event = f"critic-{status}"
    else:
        event = f"meta-{status}"

    _append_progress(PROGRESS_TEMPLATE.format(
        ts=_now(), input_id=input_id, event=event, stage=stage, ver=ver,
        status=status, score=score, feedback=feedback,
    ))


def _handle_content_write(file_path: Path, input_id: str, stage: str, ver: int) -> None:
    """Log a content write; warn if sibling meta is missing."""
    meta = _read_meta_block(file_path)
    if meta is None:
        logger.warning("content write at %s has no sibling .meta.json; possible missing meta", file_path)
        _append_progress(PROGRESS_TEMPLATE.format(
            ts=_now(), input_id=input_id, event="content-write-no-meta",
            stage=stage, ver=ver, status="warn", score=0.0,
            feedback="no sibling .meta.json",
        ))
    else:
        _append_progress(PROGRESS_TEMPLATE.format(
            ts=_now(), input_id=input_id, event="content-write",
            stage=stage, ver=ver, status="ok", score=0.0, feedback="",
        ))


def post(tool_input: dict[str, Any]) -> dict[str, Any]:
    """Process a single PostToolUse event. Returns {"continue": true}."""
    file_path = tool_input.get("file_path", "")
    normalized = file_path.replace("\\", "/")

    meta_match = META_RE.match(normalized)
    if meta_match:
        input_id, stage, ver = meta_match.group(1), meta_match.group(2), int(meta_match.group(3))
        _handle_meta_write(REPO / normalized, input_id, stage, ver)
        return {"continue": True}

    content_match = CONTENT_RE.match(normalized)
    if content_match:
        input_id, stage, ver = content_match.group(1), content_match.group(2), int(content_match.group(3))
        _handle_content_write(REPO / normalized, input_id, stage, ver)
        return {"continue": True}

    return {"continue": True}


def main() -> int:
    """Entry point. Reads JSON from stdin, processes, emits continue, exits 0."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        logger.warning("PostToolUse received non-JSON payload; no-op")
        sys.stdout.write(json.dumps({"continue": True}))
        sys.stdout.flush()
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    result = post(tool_input)
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
