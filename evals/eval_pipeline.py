#!/usr/bin/env python3
"""eval_pipeline.py — Basic automated evaluation script for auto-research.

Runs completeness, coherence, and prompt injection checks on pipeline outputs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = REPO_ROOT / "outputs"


def eval_completeness(artifact: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Check that all required fields from schema are present and not empty."""
    required = schema.get("required", [])
    missing = []
    empty = []
    for key in required:
        if key not in artifact:
            missing.append(key)
        else:
            val = artifact[key]
            if val is None or val == "" or val == {} or val == []:
                empty.append(key)
    
    status = "pass" if not (missing or empty) else "fail"
    return {
        "status": status,
        "missing": missing,
        "empty": empty,
        "reason": f"Missing: {missing}, Empty: {empty}" if status == "fail" else "All required fields present"
    }


def eval_coherence(analysis: dict[str, Any], extraction: dict[str, Any]) -> dict[str, Any]:
    """Check that analyzer themes are coherent with extractor entities/facts."""
    themes = analysis.get("themes", [])
    facts = extraction.get("facts", [])
    entities = extraction.get("entities", [])
    
    if not themes:
        return {"status": "pass", "reason": "No themes to check coherence against"}
        
    grounded_count = 0
    total_themes = len(themes)
    
    fact_claims = {f.get("claim", "").lower() for f in facts}
    entity_names = {e.get("name", "").lower() for e in entities}
    
    for theme in themes:
        desc = theme.get("description", "").lower()
        supporting = [f.lower() for f in theme.get("supporting_facts", [])]
        
        # Grounded if supporting facts exist in extracted facts or theme references extracted entities
        is_grounded = False
        for sup in supporting:
            if any(sup in claim for claim in fact_claims):
                is_grounded = True
                break
        
        if not is_grounded:
            # Check if theme description mentions any extracted entities
            if any(entity in desc for entity in entity_names if len(entity) > 3):
                is_grounded = True
                
        if is_grounded:
            grounded_count += 1
            
    coherence_ratio = grounded_count / total_themes if total_themes > 0 else 1.0
    status = "pass" if coherence_ratio >= 0.5 else "fail"
    
    return {
        "status": status,
        "coherence_ratio": coherence_ratio,
        "reason": f"{grounded_count}/{total_themes} themes grounded in extracted facts/entities"
    }


def eval_injection(text: str) -> dict[str, Any]:
    """Scan input text for typical prompt injection keywords."""
    keywords = [
        "ignore previous instructions",
        "ignore all previous",
        "system prompt",
        "you are now a",
        "do not follow the pipeline",
        "override instructions"
    ]
    detected = []
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            detected.append(kw)
            
    status = "pass" if not detected else "fail"
    return {
        "status": status,
        "detected_keywords": detected,
        "reason": f"Detected injection patterns: {detected}" if detected else "No injection patterns detected"
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python evals/eval_pipeline.py <input_id>")
        sys.exit(1)
        
    input_id = sys.argv[1]
    out_dir = OUTPUTS / input_id
    if not out_dir.exists():
        print(f"Output directory not found: {out_dir}")
        sys.exit(1)
        
    print(f"=== Running basic evals for input_id: {input_id} ===")
    
    # 1. completeness
    completeness_status = "pass"
    fmt_file = out_dir / "05_format" / "v1.json"
    schema_file = REPO_ROOT / "schemas" / "05_format.json"
    if fmt_file.exists() and schema_file.exists():
        with open(fmt_file, encoding="utf-8") as f:
            artifact = json.load(f)
        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)
        res = eval_completeness(artifact, schema)
        print(f"Completeness check: {res['status'].upper()} ({res['reason']})")
        completeness_status = res["status"]
    else:
        print("Completeness check: SKIP (missing artifact/schema)")
        
    # 2. coherence
    coherence_status = "pass"
    anal_file = out_dir / "03_analyze" / "v1.json"
    ext_file = out_dir / "02_extract" / "v1.json"
    if anal_file.exists() and ext_file.exists():
        with open(anal_file, encoding="utf-8") as f:
            analysis = json.load(f)
        with open(ext_file, encoding="utf-8") as f:
            extraction = json.load(f)
        res = eval_coherence(analysis, extraction)
        print(f"Coherence check: {res['status'].upper()} ({res['reason']})")
        coherence_status = res["status"]
    else:
        print("Coherence check: SKIP (missing analyze/extract winner)")
        
    # 3. injection
    injection_status = "pass"
    ingest_file = out_dir / "01_ingest" / "v1.json"
    if ingest_file.exists():
        with open(ingest_file, encoding="utf-8") as f:
            ingest_data = json.load(f)
        text = ingest_data.get("text", "")
        res = eval_injection(text)
        print(f"Injection check: {res['status'].upper()} ({res['reason']})")
        injection_status = res["status"]
    else:
        print("Injection check: SKIP (missing ingest txt)")
        
    if completeness_status == "fail" or coherence_status == "fail" or injection_status == "fail":
        print("\nVerdict: FAIL")
        sys.exit(1)
    else:
        print("\nVerdict: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
