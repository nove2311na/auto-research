"""Smoke test: refactored validator with new llm_judge_score param.
Simulates critic-as-LLM-judge flow. Run from project root via .venv python.
"""
import json
from pathlib import Path
from tools.artifact_io import write_meta, build_meta
from tools.validator import validate_artifact

INPUT_ID = "smoke0001"
STAGE = "02_extract"
out_dir = Path(f"outputs/{INPUT_ID}/{STAGE}")
out_dir.mkdir(parents=True, exist_ok=True)

artifact = {
    "entities": [{"name": "Anthropic", "type": "org", "mentions": 3}],
    "facts": [{"claim": "Claude Code CLI uses local auth",
               "evidence_quote": "no API key needed; uses existing Claude Code CLI auth"}],
    "quotes": [],
}

def fresh(v: int, art: dict) -> None:
    (out_dir / f"v{v}.json").write_text(json.dumps(art, indent=2))
    write_meta(INPUT_ID, STAGE, v,
               build_meta(input_id=INPUT_ID, stage=STAGE, version=v,
                          producer="extractor", parent_ref="01_ingest/v1.txt"))

print("--- 1) critic pre-check: schema+completeness, judge=None ---")
fresh(1, artifact)
pre = validate_artifact(INPUT_ID, STAGE, 1, ext="json", llm_judge_score=None)
print(json.dumps({"status": pre["status"],
                  "checks": {k: v["status"] for k,v in pre["checks"].items()}}, indent=2))
assert pre["status"] == "pass", f"expected pass: {pre}"

print("\n--- 2) critic scores 0.85, re-call to record ---")
r = validate_artifact(INPUT_ID, STAGE, 1, ext="json", llm_judge_score=0.85)
print(json.dumps({"status": r["status"], "score": r["score"], "feedback": r["feedback"]}, indent=2))
assert r["status"] == "pass" and r["score"] == 0.85

print("\n--- 3) critic scores 0.5 (below 0.7 threshold) -> fail ---")
v2_art = {**artifact, "entities": artifact["entities"] + [{"name": "hcom", "type": "tool", "mentions": 1}]}
fresh(2, v2_art)
fail = validate_artifact(INPUT_ID, STAGE, 2, ext="json", llm_judge_score=0.5)
print(json.dumps({"status": fail["status"], "score": fail["score"], "feedback": fail["feedback"]}, indent=2))
assert fail["status"] == "fail"

print("\n--- 4) empty arrays must NOT fail completeness ---")
empty = {
    "entities": [{"name": "X", "type": "concept", "mentions": 1}],
    "facts": [],
    "quotes": [],
}
fresh(3, empty)
r3 = validate_artifact(INPUT_ID, STAGE, 3, ext="json", llm_judge_score=0.75)
print(json.dumps({"status": r3["status"],
                  "checks": {k: v["status"] for k,v in r3["checks"].items()}}, indent=2))
assert r3["status"] == "pass", f"empty arrays broke completeness: {r3}"

print("\n--- 5) all metas on disk ---")
for v in [1, 2, 3]:
    m = json.loads((out_dir / f"v{v}.meta.json").read_text())
    print(f"v{v}: status={m['validation']['status']} score={m['validation']['score']}")

print("\nALL SMOKE CHECKS PASSED")
