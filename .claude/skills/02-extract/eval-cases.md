# Eval cases — 02-extract

## Case E1: 3 options visibly different
- **Input:** 01_ingest/v1.txt (the QEC dossier)
- **Expected:** options/A (entity-first), options/B (fact-first), options/C (quote-first) each prioritize differently
- **Pass:** critic scores all 3 >= 0.7; pick_winner picks one; stage-root v1.json written
- **Smoke:** `scripts/smoke_v2.py:74-86` (single-winner variant only — 3-option variant is V2 follow-up)

## Case E2: empty input
- **Input:** 01_ingest/v1.txt is empty
- **Expected:** all options = {entities:[], facts:[], quotes:[]}; meta.feedback = "empty input"
- **Pass:** schema check passes (arrays may be empty); critic fails; orchestrator halts

## Case E3: input too long (>50K tokens)
- **Input:** 01_ingest/v1.txt is huge
- **Expected:** extract from first 50K; meta.feedback = "truncated at 50K tokens"
- **Pass:** options written; meta.feedback documents truncation
