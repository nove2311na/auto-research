"""run_eval.py — score a single eval case against the 8-criterion rubric.

Usage:
    python -m research_pipeline.tools.evals.run_eval <case.json> [--rubric evals/rubric/eval_rubric.defaults.json]
"""
from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from research_pipeline.paths import EVALS, OUTPUTS, REPO_ROOT

REPO = REPO_ROOT
RUBRIC_PATH = EVALS / "rubric" / "eval_rubric.defaults.json"
SCORECARDS = EVALS / "scorecards"


def _load_rubric(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _evaluate_run(input_id: str, expected_outputs: dict[str, Any]) -> dict[str, float]:
    """Helper to evaluate the actual files written to outputs/<input_id> against expected constraints."""
    scores = {
        "correctness": 0.8,
        "completeness": 0.8,
        "grounding": 0.8,
        "safety": 0.8,
        "maintainability": 0.8,
        "testability": 0.8,
        "cost": 0.8,
        "reproducibility": 0.8,
    }

    if not input_id or not expected_outputs:
        return scores

    run_dir = OUTPUTS / input_id
    if not run_dir.exists():
        # If the directory doesn't exist, we can't evaluate. Correctness and completeness are 0.
        return {
            "correctness": 0.0,
            "completeness": 0.0,
            "grounding": 0.0,
            "safety": 0.0,
            "maintainability": 0.0,
            "testability": 0.0,
            "cost": 0.0,
            "reproducibility": 0.0,
        }

    total_expected = len(expected_outputs)
    passed_correctness = 0
    passed_completeness = 0
    grounding_score_sum = 0.0
    grounding_count = 0

    schema_check: Callable[[str, str], dict[str, Any]] | None = None
    try:
        from research_pipeline.tools.validator import schema_check as val_schema_check
        schema_check = val_schema_check
    except ImportError:
        schema_check = None

    for rel_path, constraints in expected_outputs.items():
        art_path = run_dir / rel_path
        if not art_path.exists():
            continue

        # Correctness: it exists! Let's check schema for json files
        is_correct = True
        if art_path.suffix == ".json" and schema_check is not None:
            try:
                parts = rel_path.split("/")
                stage = parts[0]
                if "options" in parts:
                    stage = "02_extract"
                check = schema_check(art_path.read_text(encoding="utf-8"), stage)
                if check.get("status") != "pass":
                    is_correct = False
            except Exception:
                is_correct = False

        if is_correct:
            passed_correctness += 1

        # Completeness: constraints matching
        is_complete = True
        try:
            if art_path.suffix == ".json":
                data = json.loads(art_path.read_text(encoding="utf-8"))
                for k, v in constraints.items():
                    if k == "min_sources" and len(data.get("sources", [])) < v or k == "min_key_findings" and len(data.get("key_findings", [])) < v or k == "min_entities" and len(data.get("entities", [])) < v or k == "min_facts" and len(data.get("facts", [])) < v or k == "min_themes" and len(data.get("themes", [])) < v or k == "min_gaps" and len(data.get("gaps", [])) < v or k == "max_contradictions" and len(data.get("contradictions", [])) > v or k == "min_diagrams" and len(data.get("diagrams", [])) < v or k == "min_theses" and len(data.get("theses", [])) < v or k == "has_summary" and not data.get("summary") or k == "has_diagrams" and not data.get("diagrams") or k == "has_theses" and not data.get("theses"):
                        is_complete = False
            elif art_path.suffix in (".txt", ".md"):
                text = art_path.read_text(encoding="utf-8")
                for k, v in constraints.items():
                    if k == "min_length" and len(text) < v or k == "min_lines" and len(text.splitlines()) < v:
                        is_complete = False
        except Exception:
            is_complete = False

        if is_complete:
            passed_completeness += 1

        # Grounding check: verify citations resolve to source list indexes
        if "00_research" in rel_path and art_path.suffix == ".json":
            try:
                import re
                data = json.loads(art_path.read_text(encoding="utf-8"))
                synthesis = data.get("synthesis", "")
                sources = data.get("sources", [])
                citations = [int(x) for x in re.findall(r"\[(\d+)\]", synthesis)]
                if citations and sources:
                    valid_c = [c for c in citations if 1 <= c <= len(sources)]
                    grounding_score_sum += len(valid_c) / len(citations)
                else:
                    grounding_score_sum += 1.0
                grounding_count += 1
            except Exception:
                pass

    if total_expected > 0:
        scores["correctness"] = passed_correctness / total_expected
        scores["completeness"] = passed_completeness / total_expected
    if grounding_count > 0:
        scores["grounding"] = grounding_score_sum / grounding_count
    elif total_expected > 0:
        # If expected outputs were found but not research stage specifically, default to 0.85
        scores["grounding"] = 0.85

    # Check prd.json for cost/retries
    prd_path = REPO / "prd.json"
    if prd_path.exists():
        try:
            prd = json.loads(prd_path.read_text(encoding="utf-8"))
            retries = prd.get("retries", {})
            total_retries = sum(retries.values())
            scores["cost"] = max(0.2, 1.0 - (total_retries * 0.15))
        except Exception:
            pass

    return scores


def _score_case(case: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    """Return a scorecard dict. The actual scoring uses gates + LLM-judge + manual."""
    gates = case.get("gates", {})
    evidence = case.get("evidence", [])

    # Get dynamic scores if expected_outputs exist
    input_id = case.get("input_id")
    expected_outputs = case.get("expected_outputs")
    dynamic_scores = _evaluate_run(input_id, expected_outputs) if (input_id and expected_outputs) else {}

    criteria = rubric["criteria"]
    weights = rubric.get("weights", {})

    scores = {}
    for k in criteria:
        if k in case.get("rubric_scores", {}):
            scores[k] = float(case["rubric_scores"][k])
        elif k in dynamic_scores:
            scores[k] = float(dynamic_scores[k])
        else:
            scores[k] = 0.8

    weighted = [scores[k] * weights.get(k, 1.0) for k in scores]
    weight_sum = sum(weights.get(k, 1.0) for k in scores) or 1.0
    final = sum(weighted) / weight_sum

    pass_t = rubric["thresholds"]["pass"]
    warn_t = rubric["thresholds"]["warn"]
    if final >= pass_t:
        status = "pass"
    elif final >= warn_t:
        status = "warn"
    else:
        status = "fail"

    return {
        "run_id": case.get("id", "unknown"),
        "agent": case.get("agent", "unknown"),
        "task": case.get("task", case.get("id", "unknown")),
        "rubric_scores": scores,
        "final_score": round(final, 4),
        "gates": gates,
        "evidence": evidence,
        "final_status": status,
    }


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    case_path = Path(args[0])
    rubric_path = Path(args[1]) if len(args) > 1 else RUBRIC_PATH

    case = json.loads(case_path.read_text(encoding="utf-8"))
    rubric = _load_rubric(rubric_path)
    card = _score_case(case, rubric)

    SCORECARDS.mkdir(parents=True, exist_ok=True)
    out = SCORECARDS / f"{card['run_id']}.json"
    out.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} status={card['final_status']} score={card['final_score']}")
    return 0 if card["final_status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
