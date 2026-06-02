# Eval cases — 06-validate

## Case V1: pass (score 0.85)
- **Input:** 02_extract/options/A/v1.json valid, 5 entities, 8 facts
- **Expected:** validation.status = "pass"; score = 0.85
- **Pass:** meta.validation block filled
- **Smoke:** `scripts/smoke_v2.py:215-222`

## Case V2: fail (schema violation)
- **Input:** 02_extract/options/A/v1.json missing required "entities" field
- **Expected:** validation.status = "fail"; feedback names the missing field
- **Pass:** fail surfaces the exact field name

## Case V3: fail (below threshold)
- **Input:** valid schema, LLM-judge = 0.5
- **Expected:** validation.status = "fail"; feedback = "score 0.50 < threshold 0.70"
- **Pass:** threshold check fires

## Case V4: multi-option tie
- **Input:** 3 options with same LLM-judge score
- **Expected:** critic tiebreaks on schema+completeness; documents tiebreak in feedback
- **Pass:** pick_winner called with deterministic order; feedback explains
