# Rubric — 04-synthesize

| Criterion | Weight | What "good" looks like for 04-synthesize |
|---|---|---|
| Correctness | 1.0 | summary is 1-3 sentences; insights 3-7; diagrams >= 2 (1 flowchart + 1 mindmap); theses >= 2 |
| Completeness | 1.0 | narrative is 1-3 paragraphs (not bullet points); every theme from 03_analyze has at least 1 insight or thesis |
| Grounding | 1.0 | no new facts (synthesize, don't fabricate); thesis.evidence drawn from 02_extract.facts or 00_research.key_findings |
| Safety | 0.7 | no leaked PII; counterarguments are intellectually honest (not straw men) |
| Maintainability | 0.8 | summary is concise; diagram.code is Mermaid-valid (no syntax errors) |
| Testability | 1.0 | smoke S1 (canonical) reproduces; S2 (empty) returns the halt shape; S3 (bad Mermaid) fails LLM-judge |
| Cost | 0.7 | Mermaid diagrams are 5-15 lines each (not 50+); insights are 1-2 sentences |
| Reproducibility | 1.0 | same 03_analyze produces same number of insights + diagrams + theses; phrasing may differ |

**Thresholds:** pass >= 0.8, warn 0.6-0.8, fail < 0.6.

**Special note:** diagrams[].code MUST be valid Mermaid. The LLM-judge checks this.
