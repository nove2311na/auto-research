# Rubric — 06-validate (the critic)

| Criterion | Weight | What "good" looks like for 06-validate |
|---|---|---|
| Correctness | 1.0 | validation block has all 5 fields; status is pass\|fail; checks has all 3 keys; score in [0,1] |
| Completeness | 1.0 | every meta.json for a stage has a validation block (no skipped stages) |
| Grounding | 1.0 | feedback is specific (names the missing field / the low score / the tiebreak reason); not "all good" |
| Safety | 1.0 | never edits v<N>.json content; only meta + stage-root copy via pick_winner; never overrules a pass; never underrules a fail |
| Maintainability | 0.8 | feedback is short (<=500 chars); no PII leaked in feedback |
| Testability | 1.0 | smoke V1 (pass) reproduces; V2 (schema fail) names the field; V3 (threshold fail) cites the score; V4 (tie) tiebreaks deterministically |
| Cost | 0.9 | 1 LLM-judge call per stage; no retry on tie; no re-read of full artifact unless score is borderline |
| Reproducibility | 1.0 | LLM-judge score variance < 0.1 across 5 reruns (per smoke_llm_judge.py) |

**Thresholds:** pass >= 0.8, warn 0.6-0.8, fail < 0.6.

**Special note:** the critic is the only validator. Self-validation is forbidden (per agent hard rules). All 6 stages must be validated; missing = halt.
