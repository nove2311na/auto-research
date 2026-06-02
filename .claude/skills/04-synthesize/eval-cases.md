# Eval cases — 04-synthesize

## Case S1: normal 03_analyze input
- **Input:** 03_analyze/v1.json (themes+gaps+contradictions)
- **Expected:** summary 1-3 sentences; insights 3-7; diagrams >= 2 (>= 1 flowchart + >= 1 mindmap); theses >= 2
- **Pass:** schema check + completeness + LLM-judge >= 0.7
- **Smoke:** `scripts/smoke_v2.py:108-132`

## Case S2: empty 03_analyze
- **Input:** themes=[], gaps=[whole-topic-is-empty], contradictions=[]
- **Expected:** summary = "Source material had no extractable themes."; no fabricated diagrams/theses
- **Pass:** schema passes; critic fails (empty); orchestrator halts

## Case S3: Mermaid syntax error
- **Input:** normal analyze, but agent writes invalid Mermaid
- **Expected:** LLM-judge fails (0 diagrams with valid code); agent retries
- **Pass:** after retry, valid Mermaid; or halt if retries exhausted
