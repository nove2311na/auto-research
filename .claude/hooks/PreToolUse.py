"""PreToolUse hook — preflight validation of upstream stage artifacts.

Implements .docs/agentic/validation/01-pre-execution-schema.md:
  - Read JSON payload from stdin (tool_name, tool_input)
  - If the target is outputs/<id>/<stage>/v<N>.* and an upstream artifact exists
    in the same outputs/<id>/ tree, run a deterministic preflight:
      * JSON ext: tools.validator.schema_check against the upstream's schema
      * TXT  ext: assert non-empty UTF-8
  - On fail: write {"decision": "block", "reason": "..."} to stdout
  - On pass: write {"decision": "approve"} to stdout
  - Always exit 0 (Claude Code convention; non-zero exit blocks the tool)

Conventions (per .claude/rules/python.md):
  - Type hints on signatures
  - pathlib.Path over os.path
  - logging module, not print
  - Standard lib, then third-party, then local
"""
from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

logger = logging.getLogger("claude.hooks.pretooluse")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

STAGE_RE = re.compile(r"^outputs/([^/]+)/(\d{2}_[a-z]+)/v\d+\.(json|txt)$")

def _load_stage_order() -> list[str]:
    try:
        cfg = json.loads((REPO / "pipeline.json").read_text(encoding="utf-8"))
        return [s["id"] for s in cfg.get("stages", [])]
    except Exception:
        return [
            "00_research", "01_ingest", "02_extract", "03_analyze",
            "04_synthesize", "05_format",
        ]

STAGE_ORDER = _load_stage_order()


def _prev_stage(stage: str) -> str | None:
    """Return the previous stage id in the pipeline, or None if `stage` is the first."""
    if stage not in STAGE_ORDER:
        return None
    idx = STAGE_ORDER.index(stage)
    if idx == 0:
        return None
    return STAGE_ORDER[idx - 1]


def _upstream_path(input_id: str, prev_stage: str) -> Path | None:
    """Locate the upstream artifact on disk. Returns the path or None if missing."""
    for ext in ("json", "txt", "md"):
        candidate = REPO / "outputs" / input_id / prev_stage / f"v1.{ext}"
        if candidate.exists():
            return candidate
    options_dir = REPO / "outputs" / input_id / prev_stage / "options"
    if options_dir.exists():
        for option_dir in sorted(options_dir.iterdir()):
            for ext in ("json", "txt", "md"):
                candidate = option_dir / f"v1.{ext}"
                if candidate.exists():
                    return candidate
    return None


def _emit(decision: str, reason: str = "") -> None:
    """Emit a JSON decision to stdout and exit 0."""
    payload: dict[str, Any] = {"decision": decision}
    if reason:
        payload["reason"] = reason
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()


def preflight(tool_input: dict[str, Any]) -> dict[str, Any]:
    """Run the preflight check. Returns {"decision": "approve"|"block", "reason": str}."""
    file_path = tool_input.get("file_path", "")
    match = STAGE_RE.match(file_path.replace("\\", "/"))
    if not match:
        return {"decision": "approve"}

    input_id, stage, ext = match.group(1), match.group(2), match.group(3)
    prev = _prev_stage(stage)
    if prev is None:
        return {"decision": "approve"}

    upstream = _upstream_path(input_id, prev)
    if upstream is None:
        return {"decision": "approve"}

    try:
        content = upstream.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"decision": "block", "reason": f"upstream {upstream} is not valid UTF-8"}

    if ext == "txt":
        if not content.strip():
            return {"decision": "block", "reason": f"upstream {upstream} is empty"}
        return {"decision": "approve"}

    try:
        from tools.validator import schema_check
        result = schema_check(content, prev)
    except Exception as exc:  # noqa: BLE001 — surface any tool/import error to the caller
        logger.warning("preflight tool import failed: %s", exc)
        return {"decision": "approve"}

    if result.get("status") == "fail":
        return {"decision": "block", "reason": f"upstream {prev} schema fail: {result.get('error', '?')}"}
    return {"decision": "approve"}


def main() -> int:
    """Entry point. Reads JSON from stdin, runs preflight, emits decision, exits 0."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        logger.warning("PreToolUse received non-JSON payload; approving by default")
        _emit("approve")
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    result = preflight(tool_input)
    _emit(result["decision"], result.get("reason", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
