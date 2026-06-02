# Rubric — 02-extract

| Criterion | Weight | What "good" looks like for 02-extract |
|---|---|---|
| Correctness | 1.0 | each option matches schemas/02_extract.json (Draft-7); all 3 options are valid JSON; pick_winner picks a valid one |
| Completeness | 1.0 | pipeline.json#02_extract.max_options options are written (1/2/3); each option has entities[] + facts[] + quotes[] |
| Grounding | 1.0 | every fact.claim has a verbatim evidence_quote; no unsourced claims; entities all mentioned in source |
| Safety | 0.8 | no PII in entities; no leaked source material in evidence_quote |
| Maintainability | 0.8 | entities are deduped across options (same entity not in 3 lists under 3 names); fact.claim is 1 sentence |
| Testability | 1.0 | smoke case E1 (canonical) reproduces; E2 (empty) doesn't crash; E3 (huge) truncates |
| Cost | 0.9 | 3 options read the same input once (no triple-re-read); options reuse entity detection where possible |
| Reproducibility | 1.0 | the same input produces 3 options with the same entity/fact counts (LLM may phrase differently) |

**Thresholds:** pass >= 0.8, warn 0.6-0.8, fail < 0.6.

**Special note:** this is the only multi-option stage; pick_winner determinism is part of reproducibility.
