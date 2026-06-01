"""End-to-end smoke test for the 6-stage pipeline.

Simulates all 6 stage agents (including the new 00_research + diagrams/theses),
runs validator on each, renders the final markdown, asserts manifest is_done.
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from tools.artifact_io import write_meta, build_meta, atomic_write
from tools.validator import validate_artifact
from tools.manifest import init_manifest, record_attempt, finalize, is_done

INPUT_ID = "smokev200"
TOPIC = "Quantum error correction 2026"

# --- 1) Simulate 00_research (researcher) ----------------------------------
research_artifact = {
    "topic": TOPIC,
    "depth": "medium",
    "queries": [
        {"query": "quantum error correction 2026 advances", "round": 1, "rationale": "broad scoping", "results_count": 8},
        {"query": "topological codes Google IBM 2025", "round": 1, "rationale": "key players", "results_count": 6},
        {"query": "surface code threshold recent papers", "round": 2, "rationale": "gap from round 1", "results_count": 5},
        {"query": "logical qubit overhead criticism", "round": 2, "rationale": "limitations", "results_count": 4},
    ],
    "sources": [
        {"url": "https://example.com/qec-review-2026", "title": "QEC Review 2026", "fetched_at": "2026-06-01T12:00:00Z",
         "excerpt": "Surface codes remain dominant; logical qubit counts crossed 1000 in 2026 demonstrations.",
         "relevance": "high"},
        {"url": "https://example.com/google-condor-2025", "title": "Google Condor Update", "fetched_at": "2026-06-01T12:01:00Z",
         "excerpt": "Google's 1000+ qubit Condor processor achieved below-threshold surface code operation.",
         "relevance": "high"},
    ],
    "synthesis": "Quantum error correction matured significantly in 2026. Surface codes dominate due to their high threshold (~1%) and planar geometry. Google's Condor and IBM's Heron R3 both demonstrated below-threshold operation with 1000+ logical qubits. Key challenges remain: logical qubit overhead (1000:1 physical:logical), real-time decoding latency, and crosstalk in 2D arrays.",
    "key_findings": [
        "Surface codes crossed the 1000 logical qubit milestone in 2026",
        "Below-threshold operation now routine for distances d=5 to d=11",
        "Real-time decoding latency remains the bottleneck for fault-tolerant gates",
    ],
    "gaps": [
        "Limited public data on long-term (week-scale) logical qubit stability",
        "Color codes largely unexplored in recent industrial demonstrations",
    ],
}

# --- 2) Simulate 01_ingest (ingestor merges dossier) ------------------------
ingest_text = f"""{TOPIC}

## Research Context

{research_artifact['synthesis']}

**Sources:**
[1] {research_artifact['sources'][0]['title']} — {research_artifact['sources'][0]['url']}
[2] {research_artifact['sources'][1]['title']} — {research_artifact['sources'][1]['url']}

**Key findings:**
- {research_artifact['key_findings'][0]}
- {research_artifact['key_findings'][1]}
- {research_artifact['key_findings'][2]}
"""
ingest_meta = {
    "text": ingest_text,
    "metadata": {
        "source_type": "text",
        "source_ref": "inputs/inbox/qec.txt",
        "size_bytes": len(ingest_text),
        "research_ref": "00_research/v1.json",
    },
}

# --- 3) Simulate 02_extract (extractor, multi-option) ----------------------
extract_winner = {
    "entities": [
        {"name": "Google", "type": "org", "mentions": 4},
        {"name": "IBM", "type": "org", "mentions": 3},
        {"name": "Surface code", "type": "concept", "mentions": 5},
        {"name": "Condor processor", "type": "product", "mentions": 2},
    ],
    "facts": [
        {"claim": "Surface codes have ~1% threshold", "evidence_quote": "high threshold (~1%)", "confidence": "high"},
        {"claim": "1000+ logical qubits demonstrated in 2026", "evidence_quote": "logical qubit counts crossed 1000", "confidence": "high"},
    ],
    "quotes": [],
}

# --- 4) Simulate 03_analyze (analyzer) --------------------------------------
analyze_artifact = {
    "themes": [
        {"name": "surface code dominance", "description": "Surface codes are the de facto industrial QEC",
         "supporting_facts": ["Surface codes have ~1% threshold"]},
        {"name": "threshold achievement", "description": "Multiple platforms crossed below-threshold operation",
         "supporting_facts": ["1000+ logical qubits demonstrated in 2026"]},
    ],
    "gaps": [
        {"description": "Long-term stability of logical qubits",
         "what_would_fill_it": "Multi-week coherence measurements on hardware"},
    ],
    "contradictions": [
        {"claim_a": "Academic literature claims overhead reduction",
         "claim_b": "Industrial practice still uses 1000:1 physical-to-logical ratio",
         "explanation": "Decoding overhead and syndrome measurement costs may offset theoretical savings"},
    ],
}

# --- 5) Simulate 04_synthesize (synthesizer adds diagrams+theses) ----------
synth_artifact = {
    "summary": "Quantum error correction crossed industrial viability in 2026 with 1000+ logical qubits via surface codes, but overhead and decoding latency remain critical bottlenecks.",
    "insights": [
        {"insight": "Surface codes are the de facto standard for 2026 industrial QEC",
         "grounding": "themes: surface code dominance, industrial scaling", "novelty": "medium"},
    ],
    "narrative": "The past year marked a turning point for quantum error correction, as multiple platforms achieved below-threshold operation with hundreds to thousands of logical qubits. Yet the path to fault-tolerant quantum computing still hinges on solving the decoder-latency problem and reducing physical-to-logical overhead.",
    "diagrams": [
        {"type": "flowchart", "title": "QEC Pipeline",
         "code": "flowchart LR\n  A[Physical Qubits] --> B[Surface Code Encoding]\n  B --> C[Stabilizer Measurements]\n  C --> D[Real-time Decoder]\n  D --> E[Logical Qubit]",
         "description": "The error correction cycle from physical measurement to logical qubit output."},
        {"type": "mindmap", "title": "QEC Landscape 2026",
         "code": "mindmap\n  root((QEC 2026))\n    Codes\n      Surface\n      Color\n      Subsystem\n    Players\n      Google\n      IBM\n      IonQ\n    Challenges\n      Overhead\n      Decoding\n      Crosstalk"},
    ],
    "theses": [
        {"statement": "Surface codes will dominate industrial QEC for the next 3-5 years",
         "evidence": ["1000+ logical qubit demonstrations in 2026", "Mature fabrication processes favor planar codes", "Below-threshold operation routine"],
         "counterarguments": ["Color codes have better transversal gate sets", "LDPC codes could leapfrog surface codes if overhead drops"],
         "confidence": "high"},
        {"statement": "Decoder latency, not qubit count, is the real bottleneck to fault tolerance",
         "evidence": ["Real-time decoding required for syndrome extraction cycles", "Classical hardware scaling limited by interconnect bandwidth"],
         "counterarguments": ["FPGA-based decoders already operate at MHz rates for small codes", "ML decoders may unlock latency gains"],
         "confidence": "medium"},
    ],
}

# --- 6) Simulate 05_format (formatter) -------------------------------------
format_json = {
    "summary": synth_artifact["summary"],
    "entities": extract_winner["entities"],
    "facts": [{"claim": f["claim"], "source": f["evidence_quote"]} for f in extract_winner["facts"]],
    "analysis": analyze_artifact,
    "insights": [i["insight"] for i in synth_artifact["insights"]],
    "references": [s["url"] for s in research_artifact["sources"]],
    "diagrams": synth_artifact["diagrams"],
    "theses": synth_artifact["theses"],
}

# Render markdown
def render_md(f: dict) -> str:
    md = [f"# Research Report: {TOPIC}", "", f"## Summary", "", f["summary"], "",
          "## Key Insights", ""]
    for ins in f["insights"]:
        md.append(f"- {ins}")
    md += ["", "## Entities", ""]
    for e in f["entities"]:
        md.append(f"- **{e['name']}** ({e['type']}, {e['mentions']} mentions)")
    md += ["", "## Facts", ""]
    for fa in f["facts"]:
        md.append(f"- {fa['claim']} — _{fa['source']}_")
    md += ["", "## Analysis", ""]
    for th in f["analysis"]["themes"]:
        md.append(f"- **{th['name']}** — {th.get('description', '')}")
    md.append("")
    for g in f["analysis"]["gaps"]:
        md.append(f"- Gap: {g['description']} (would need: {g.get('what_would_fill_it', '?')})")
    md.append("")
    for c in f["analysis"]["contradictions"]:
        md.append(f"- Contradiction: {c['claim_a']} ↔ {c['claim_b']} — {c.get('explanation', '')}")
    md.append("")
    md += ["## Diagrams", ""]
    for d in f["diagrams"]:
        md += [f"### {d['title']}", ""]
        if d.get("description"):
            md += [d["description"], ""]
        md += ["```mermaid", d["code"], "```", ""]
    md += ["## Theses", ""]
    for i, t in enumerate(f["theses"], 1):
        md += [f"### Thesis {i}: {t['statement']}", "",
               f"**Confidence:** {t.get('confidence', 'unspecified')}", "",
               "**Evidence:**"]
        for ev in t["evidence"]:
            md.append(f"- {ev}")
        md += ["", "**Counterarguments:**"]
        for ca in t["counterarguments"]:
            md.append(f"- {ca}")
        md += [""]
    md += ["## References", ""]
    for r in f["references"]:
        md.append(f"- {r}")
    return "\n".join(md)

# --- Write all artifacts + run validator per stage -------------------------
out = Path(f"outputs/{INPUT_ID}")
init_manifest(INPUT_ID, input_hash="abc123def456", input_source="text",
              input_ref="inputs/inbox/qec.txt", size_bytes=len(ingest_text))

stages_artifacts = {
    "00_research": (research_artifact, "json", "researcher"),
    "01_ingest":   (ingest_meta,       "json", "ingestor"),
    "02_extract":  (extract_winner,    "json", "extractor"),
    "03_analyze":  (analyze_artifact,  "json", "analyzer"),
    "04_synthesize": (synth_artifact,  "json", "synthesizer"),
    "05_format":   (format_json,       "json", "formatter"),
}

print("=" * 60)
print("Running critic on each stage with simulated LLM-judge scores")
print("=" * 60)
all_pass = True
for stage, (artifact, ext, producer) in stages_artifacts.items():
    sdir = out / stage
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / f"v1.{ext}").write_text(json.dumps(artifact, indent=2))
    write_meta(INPUT_ID, stage, 1,
               build_meta(input_id=INPUT_ID, stage=stage, version=1,
                          producer=producer, parent_ref="00_research/v1.json" if stage != "00_research" else None))
    score = 0.85
    result = validate_artifact(INPUT_ID, stage, 1, ext=ext, llm_judge_score=score)
    record_attempt(INPUT_ID, stage, 1, result["status"], score=result["score"], feedback=result["feedback"])
    status_icon = "PASS" if result["status"] == "pass" else "FAIL"
    print(f"  {stage:18s} {status_icon}  score={result['score']:.2f}")
    if result["status"] != "pass":
        all_pass = False
        print(f"     feedback: {result['feedback']}")

# Write v1.md for 05_format
md = render_md(format_json)
(out / "05_format" / "v1.md").write_text(md)

# --- Assertions ------------------------------------------------------------
print("\n" + "=" * 60)
print("Assertions")
print("=" * 60)

# 1. All stages passed
assert all_pass, "at least one stage failed"
print("  [ok] all 6 stages passed critic")

# 2. Manifest has 6 stages
m = json.loads((out / "manifest.json").read_text())
stage_ids = [s["id"] for s in m["stages"]]
assert len(stage_ids) == 6, f"expected 6 stages, got {len(stage_ids)}"
print(f"  [ok] manifest has 6 stages: {stage_ids}")

# 3. Each stage has a winner
stages_by_id = {s["id"]: s for s in m["stages"]}
for stage in ["00_research", "01_ingest", "02_extract", "03_analyze", "04_synthesize", "05_format"]:
    assert stages_by_id[stage].get("winner"), f"stage {stage} has no winner"
print("  [ok] every stage has winner=v1")

# 4. Finalize and check is_done
finalize(INPUT_ID)
assert is_done(INPUT_ID), "manifest not done after finalize"
print("  [ok] manifest.is_done() = True")

# 5. v1.md has Mermaid blocks
md_text = (out / "05_format" / "v1.md").read_text()
mermaid_count = md_text.count("```mermaid")
assert mermaid_count == 2, f"expected 2 mermaid blocks, got {mermaid_count}"
print(f"  [ok] v1.md has {mermaid_count} Mermaid blocks")

# 6. v1.md has Theses section
assert "## Theses" in md_text
thesis_count = md_text.count("### Thesis ")
assert thesis_count == 2, f"expected 2 thesis headers, got {thesis_count}"
print(f"  [ok] v1.md has {thesis_count} thesis sections")

# 7. ingest merged research dossier
ingest_text_on_disk = json.loads((out / "01_ingest" / "v1.json").read_text())["text"]
assert "## Research Context" in ingest_text_on_disk
assert "[1]" in ingest_text_on_disk and "[2]" in ingest_text_on_disk
print("  [ok] 01_ingest merged research dossier (Research Context + [N] citations)")

# 8. research_ref propagated
ingest_meta_on_disk = json.loads((out / "01_ingest" / "v1.json").read_text())["metadata"]
assert ingest_meta_on_disk.get("research_ref") == "00_research/v1.json"
print("  [ok] metadata.research_ref = '00_research/v1.json'")

# 9. v1.json has diagrams + theses
fmt_on_disk = json.loads((out / "05_format" / "v1.json").read_text())
assert len(fmt_on_disk["diagrams"]) == 2
assert len(fmt_on_disk["theses"]) == 2
print(f"  [ok] 05_format/v1.json has {len(fmt_on_disk['diagrams'])} diagrams + {len(fmt_on_disk['theses'])} theses")

# 10. completed_at filled
m = json.loads((out / "manifest.json").read_text())
assert m.get("completed_at"), "completed_at not set"
print(f"  [ok] manifest.completed_at = {m['completed_at']}")

print("\n" + "=" * 60)
print("ALL V2 SMOKE CHECKS PASSED")
print("=" * 60)
