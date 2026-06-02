# Regression cases

Each case = a previously-broken scenario. The pipeline MUST keep passing them.

## Cases

- `empty-input.json` — 01_ingest input is empty; downstream stages must not crash, must fail loudly.
- `3-option-extract.json` — 02_extract produces 3 visibly different options; pick_winner picks deterministically.
- `ambiguous-topic.json` — 00_research input is "AI"; disambiguation noted in gaps.
- `mermaid-syntax-error.json` — 04_synthesize writes invalid Mermaid; LLM-judge catches it; retry succeeds.
- `duplicate-urls.json` — 00_research source dedup by URL is enforced; same URL never fetched twice.

Each file = `{id, setup, expected_failure_mode, pass_criteria}`.
