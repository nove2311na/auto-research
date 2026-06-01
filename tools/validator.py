"""validator.py — schema + completeness + LLM-as-judge checks.

Used by the critic agent. Two of the three checks are deterministic (schema,
completeness); the third is an LLM call. The critic only writes the meta after
all three finish.

Usage:
    from tools.validator import validate_artifact
    result = validate_artifact(input_id, stage, version, ext="json", option=None)
    # -> {"status": "pass|fail", "score": 0.0..1.0, "feedback": "...", "checks": {...}}
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

from tools.artifact_io import (
    OUTPUTS, REPO, read_artifact, read_meta, stage_dir, write_meta, now_iso,
)

SCHEMAS = REPO / "schemas"


def _llm_judge_threshold() -> float:
    """Read pipeline.json → critic.llm_judge_threshold. Default 0.7."""
    try:
        cfg = json.loads((REPO / "pipeline.json").read_text())
        return float(cfg.get("critic", {}).get("llm_judge_threshold", 0.7))
    except Exception:
        return 0.7


def load_schema(stage: str) -> dict:
    """Load the JSON schema for a stage id (e.g. '01_ingest' or '01_ingest.json')."""
    name = stage if stage.endswith(".json") else f"{stage}.json"
    p = SCHEMAS / name
    if not p.exists():
        raise FileNotFoundError(f"schema not found: {p}")
    return json.loads(p.read_text())


def schema_check(content: str, stage: str) -> dict:
    """Validate JSON content against the stage's schema. Returns a check dict."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return {"status": "fail", "error": f"not valid JSON: {e}"}
    try:
        schema = load_schema(stage)
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
    except FileNotFoundError as e:
        return {"status": "fail", "error": str(e)}
    if errors:
        # Concise error message: each error's path + message, max 5
        msgs = []
        for err in errors[:5]:
            path = "/".join(str(p) for p in err.absolute_path) or "<root>"
            msgs.append(f"{path}: {err.message}")
        return {"status": "fail", "error": "; ".join(msgs)}
    return {"status": "pass", "error": ""}


def completeness_check(content: str, stage: str) -> dict:
    """Check that the top-level required fields are present and non-trivial.

    "Non-trivial" means: not null, not empty string, not empty object. Empty
    arrays ARE allowed — "no quotes found" is a legitimate answer, not a
    failure. Use the LLM-judge check for "this array is too small" quality
    concerns.
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return {"status": "fail", "error": f"not valid JSON: {e}"}
    schema = load_schema(stage)
    required = schema.get("required", [])
    missing: list[str] = []
    empty: list[str] = []
    for key in required:
        if key not in data:
            missing.append(key)
            continue
        v = data[key]
        if v is None or v == "" or v == {}:
            empty.append(key)
    if missing or empty:
        msg = []
        if missing:
            msg.append(f"missing: {missing}")
        if empty:
            msg.append(f"empty: {empty}")
        return {"status": "fail", "error": "; ".join(msg)}
    return {"status": "pass", "error": ""}


def validate_artifact(
    input_id: str,
    stage: str,
    version: int,
    ext: str = "json",
    option: str | None = None,
    *,
    llm_judge_score: float | None = None,
) -> dict:
    """Run schema + completeness checks. The critic agent provides the LLM-judge
    score directly (it is itself a Claude session, no SDK needed); we just record it.

    Pass llm_judge_score=None to skip that check; pass 0.0-1.0 to record it.
    """
    content = read_artifact(input_id, stage, version, ext=ext, option=option)
    checks: dict[str, dict] = {}

    if ext == "json":
        s = schema_check(content, stage)
        checks["schema"] = s
        c = completeness_check(content, stage)
        checks["completeness"] = c
    else:
        # Plain-text stages (01_ingest is .txt). Schema/completeness don't apply.
        checks["schema"] = {"status": "skip", "error": "non-JSON stage"}
        checks["completeness"] = {"status": "skip", "error": "non-JSON stage"}

    if llm_judge_score is None:
        checks["llm_judge"] = {"status": "skip", "error": "not provided"}
    else:
        threshold = _llm_judge_threshold()
        passed = llm_judge_score >= threshold
        checks["llm_judge"] = {
            "status": "pass" if passed else "fail",
            "score": llm_judge_score,
            "error": "" if passed else f"score {llm_judge_score:.2f} < threshold {threshold:.2f}",
        }

    # Aggregate
    failed = [name for name, c in checks.items() if c.get("status") == "fail"]
    if failed:
        status = "fail"
        first_err = next((checks[n]["error"] for n in failed if checks[n].get("error")), "")
        feedback = f"failed checks: {failed}. first error: {first_err}"
        score = 0.0
    else:
        status = "pass"
        # Use the LLM-judge score if provided, else 0.8 as neutral default
        judge = checks.get("llm_judge", {})
        if judge.get("status") == "pass" and isinstance(judge.get("score"), (int, float)):
            score = judge["score"]
        else:
            score = 0.8
        feedback = "all checks passed"

    # Update meta
    meta = read_meta(input_id, stage, version, option) or {}
    meta["validation"] = {
        "status": status,
        "validator": "critic",
        "validated_at": now_iso(),
        "score": score,
        "feedback": feedback,
        "checks": {k: v.get("status", "unknown") for k, v in checks.items()},
    }
    write_meta(input_id, stage, version, meta, option)

    return {"status": status, "score": score, "feedback": feedback, "checks": checks}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python -m tools.validator <input_id> <stage> <version> [ext] [option]")
        sys.exit(1)
    inp = sys.argv[1]
    stg = sys.argv[2]
    ver = int(sys.argv[3])
    ext = sys.argv[4] if len(sys.argv) > 4 else "json"
    opt = sys.argv[5] if len(sys.argv) > 5 else None
    print(json.dumps(validate_artifact(inp, stg, ver, ext, opt), indent=2))
