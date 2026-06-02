# Rubric — 03-analyze

| Criterion | Weight | What "good" looks like for 03-analyze |
|---|---|---|
| Correctness | 1.0 | themes/gaps/contradictions count within schema bounds; every theme has supporting_facts |
| Completeness | 1.0 | themes 2-6; gaps 1-5; contradictions 0-3; at least one gap (the "missing" call) |
| Grounding | 1.0 | every supporting_facts entry is verbatim from 02_extract.facts[].claim; contradictions are real (not just different angles) |
| Safety | 0.7 | no PII in claims; no fabricated facts |
| Maintainability | 0.8 | theme names are short (<=40 chars); descriptions are 1 line |
| Testability | 1.0 | smoke A1 (canonical) reproduces; A2 (empty) returns the halt shape; A3 (brief) has 1 theme |
| Cost | 0.9 | 1 read of 02_extract/v1.json; no re-extraction |
| Reproducibility | 1.0 | same 02_extract produces same themes (LLM may phrase differently, but count + grounding should match) |

**Thresholds:** pass >= 0.8, warn 0.6-0.8, fail < 0.6.
