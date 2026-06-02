# Rubric — 05-format

| Criterion | Weight | What "good" looks like for 05-format |
|---|---|---|
| Correctness | 1.0 | v1.json matches schemas/05_format.json; v1.md renders correctly (every section present); meta has all required fields |
| Completeness | 1.0 | every field in v1.json traces to an upstream artifact; nothing fabricated; all 3 (json/md/meta) written |
| Grounding | 1.0 | summary is verbatim from 04_synthesize.summary (modulo polish); no new facts; v1.md agrees with v1.json |
| Safety | 0.7 | no PII; finalize NOT called until critic passes |
| Maintainability | 0.8 | Markdown is human-readable (not a JSON dump); section order is consistent; ```mermaid wrapper added by formatter not synthesizer |
| Testability | 1.0 | smoke F1 (canonical) reproduces; F2 (missing upstream) halts; F3 (critic fail) does not call finalize |
| Cost | 0.7 | 1 read per upstream artifact; no double-read; no retry on trivial v1.md issues |
| Reproducibility | 1.0 | same 04_synthesize + 03_analyze + 02_extract produces same v1.json (modulo entity dedup tiebreak order) |

**Thresholds:** pass >= 0.8, warn 0.6-0.8, fail < 0.6.

**Special note:** This is the LAST stage. After critic pass, the formatter calls `tools.manifest.finalize`. Critic fail = no finalize.
