"""Output gates that run after a stage writes an artifact.

All gates return a GateResult dict (status/summary/evidence/risks).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _ok(summary: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": "pass", "summary": summary, "evidence": evidence or [], "risks": []}


def _fail(summary: str, evidence: list[str], risks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": "fail", "summary": summary, "evidence": evidence, "risks": risks}


def json_schema_gate(artifact_path: Path, schema_path: Path) -> dict[str, Any]:
    """Validate artifact JSON against stage schema (Draft-7)."""
    if not artifact_path.exists():
        return _fail(
            f"artifact missing: {artifact_path}",
            [str(artifact_path)],
            [{"severity": "high", "description": "artifact not on disk", "required_fix": "write it"}],
        )
    if not schema_path.exists():
        return _fail(
            f"schema missing: {schema_path}",
            [str(schema_path)],
            [{"severity": "high", "description": "schema not on disk", "required_fix": "author it"}],
        )
    try:
        spec = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return _fail(
            f"JSON parse error: {e.msg} at line {e.lineno}",
            [str(artifact_path)],
            [{"severity": "high", "description": str(e), "required_fix": "fix JSON"}],
        )
    try:
        import jsonschema
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft7Validator(schema).validate(spec)
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        return _fail(
            f"schema violation at {path}: {e.message}",
            [str(artifact_path), str(schema_path)],
            [{"severity": "high", "description": f"{path}: {e.message}", "required_fix": "fix field"}],
        )
    return _ok("schema check passed", [str(artifact_path)])


def llm_judge_gate(score: float, threshold: float) -> dict[str, Any]:
    """Threshold check on the LLM-judge score."""
    if score >= threshold:
        return _ok(f"score {score:.2f} >= threshold {threshold:.2f}", [f"score={score}"])
    return _fail(
        f"score {score:.2f} < threshold {threshold:.2f}",
        [f"score={score}"],
        [{"severity": "medium", "description": "below LLM-judge threshold",
          "required_fix": "re-run with stronger grounding; see eval-cases.md"}],
    )


def manifest_consistency_gate(manifest: dict[str, Any], stage: str, expected_winner: str | None) -> dict[str, Any]:
    """Check that manifest.stages[stage].winner matches what we expect."""
    stage_block = manifest.get("stages", {}).get(stage, {})
    winner = stage_block.get("winner", "")
    if not expected_winner:
        return _ok(f"no winner expected for {stage}", [f"manifest.winner={winner}"])
    if winner == expected_winner:
        return _ok(f"winner={winner} matches", [f"manifest.winner={winner}"])
    return _fail(
        f"winner mismatch: manifest={winner} expected={expected_winner}",
        [f"manifest.winner={winner}", f"expected={expected_winner}"],
        [{"severity": "medium", "description": "winner drift", "required_fix": "re-pick"}],
    )


def evidence_grounding_gate(artifact_path: Path, extract_path: Path, research_path: Path | None = None) -> dict[str, Any]:
    """Check that theses in synthesize/format stage are well-grounded in extract stage facts and research findings."""
    if not artifact_path.exists():
        return _fail(
            f"artifact missing: {artifact_path}",
            [str(artifact_path)],
            [{"severity": "high", "description": "artifact not on disk", "required_fix": "write it"}],
        )
    if not extract_path.exists():
        return _fail(
            f"extract file missing: {extract_path}",
            [str(extract_path)],
            [{"severity": "high", "description": "upstream extract not on disk", "required_fix": "run extract stage first"}],
        )

    try:
        artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
        extract_data = json.loads(extract_path.read_text(encoding="utf-8"))
    except Exception as e:
        return _fail(
            f"JSON load error: {e}",
            [str(artifact_path), str(extract_path)],
            [{"severity": "high", "description": str(e), "required_fix": "fix JSON"}],
        )

    theses = artifact_data.get("theses", [])
    if not theses:
        return _ok("no theses to validate", [str(artifact_path)])

    # Gather all ground truths from 02_extract
    ground_truths = []
    for fact in extract_data.get("facts", []):
        ground_truths.append(fact.get("claim", "").lower())
        ground_truths.append(fact.get("evidence_quote", "").lower())
    for q in extract_data.get("quotes", []):
        ground_truths.append(q.get("text", "").lower())

    # Gather from 00_research if available
    if research_path and research_path.exists():
        try:
            res_data = json.loads(research_path.read_text(encoding="utf-8"))
            for kf in res_data.get("key_findings", []):
                ground_truths.append(kf.lower())
            for src in res_data.get("sources", []):
                ground_truths.append(src.get("summary", "").lower())
        except Exception:
            pass

    errors = []
    evidence_checked = 0
    for idx, thesis in enumerate(theses):
        statement = thesis.get("statement", "")
        ev_list = thesis.get("evidence", [])
        if not ev_list:
            errors.append(f"Thesis {idx+1} ('{statement[:30]}...') has no evidence.")
            continue

        for ev in ev_list:
            evidence_checked += 1
            ev_lower = ev.lower()
            matched = False
            for gt in ground_truths:
                if not gt:
                    continue
                # Containment or substantial word overlap
                if gt in ev_lower or ev_lower in gt:
                    matched = True
                    break
                gt_words = {w for w in gt.split() if len(w) > 4}
                ev_words = {w for w in ev_lower.split() if len(w) > 4}
                if gt_words and ev_words:
                    overlap = gt_words.intersection(ev_words)
                    if len(overlap) >= 3:
                        matched = True
                        break

            if not matched:
                errors.append(f"Thesis {idx+1} has ungrounded evidence: '{ev[:60]}...'. No matching fact found in upstream extraction.")

    if errors:
        return _fail(
            "Evidence grounding gate failed: fabricated or ungrounded evidence detected.",
            errors,
            [{"severity": "high", "description": err, "required_fix": "ground theses strictly in extracted facts"} for err in errors]
        )

    return _ok(f"Evidence grounding check passed ({evidence_checked} evidence strings verified)", [str(artifact_path)])


def gate(input_dict: dict[str, Any]) -> dict[str, Any]:
    """Dispatcher: {gate: 'json_schema', ...} -> result."""
    gtype = input_dict.get("gate")
    if gtype == "json_schema":
        return json_schema_gate(Path(input_dict["artifact"]), Path(input_dict["schema"]))
    if gtype == "llm_judge":
        return llm_judge_gate(float(input_dict["score"]), float(input_dict["threshold"]))
    if gtype == "manifest_consistency":
        return manifest_consistency_gate(input_dict["manifest"], input_dict["stage"], input_dict.get("expected_winner"))
    if gtype == "evidence_grounding":
        res_path = Path(input_dict["research"]) if input_dict.get("research") else None
        return evidence_grounding_gate(Path(input_dict["artifact"]), Path(input_dict["extract"]), res_path)
    return _fail(f"unknown gate: {gtype}", [], [{"severity": "high", "description": "bad gate type", "required_fix": "fix input"}])
