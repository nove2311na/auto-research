# Eval cases — 00-research

## Case R1: shallow depth, 1 source (boundary)
- **Input:** topic="Quantum error correction 2026", depth=shallow
- **Expected:** v1.json with sources[].length >= 1, key_findings.length >= 3, synthesis 1-3 paragraphs
- **Pass criteria:** schema check + completeness + LLM-judge >= 0.7
- **Smoke:** `scripts/smoke_v2.py:18-45` (smokev200)

## Case R2: deep depth, ambiguous topic
- **Input:** topic="AI", depth=deep
- **Expected:** topic field is disambiguated to a specific subject (e.g. "open-weights LLM safety research as of 2026")
- **Pass criteria:** topic field is not the literal "AI"; gaps[] lists the disambiguation
- **Failure mode:** if topic field equals input verbatim, LLM-judge fails

## Case R3: WebSearch returns 0 results
- **Input:** topic="xzqvwxyz nonexistent term"
- **Expected:** dossier still produced; gaps[] records the 0-results query
- **Pass criteria:** schema check passes (sources[] may be empty, but key_findings[] non-empty by force)
- **Failure mode:** if dossier is empty + meta not written, orchestrator halts
