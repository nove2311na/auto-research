# Fixtures for 03-analyze

| File | Shape | Used by eval-case |
|---|---|---|
| `input.canonical.json` | Path to the 02_extract winner (the QEC extract) | A1 |
| `input.empty.json` | {entities:[], facts:[], quotes:[]} | A2 |
| `input.brief.json` | 1 fact, 1 entity | A3 |
| `expected_output.json` | themes + gaps + contradictions | A1 |
