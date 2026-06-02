# Eval cases — 05-format

## Case F1: all upstreams present
- **Input:** 04_synthesize + 03_analyze + 02_extract all v1.json exist
- **Expected:** v1.json + v1.md + v1.meta.json all written; finalize called after critic pass
- **Pass:** schema check + LLM-judge >= 0.7
- **Smoke:** `scripts/smoke_v2.py:135-144, 147-188`

## Case F2: missing upstream
- **Input:** 04_synthesize/v1.json absent (prior stage failed)
- **Expected:** formatter halts; tells @orch which stage failed; no partial report
- **Pass:** no v1.md written; orchestrator notified

## Case F3: critic fails
- **Input:** all upstreams present, but format itself fails schema
- **Expected:** formatter does NOT call finalize; manifest stays winner='' for 05_format
- **Pass:** meta.validation.status = "fail"; finalize NOT called
