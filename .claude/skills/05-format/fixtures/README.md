# Fixtures for 05-format

| File | Shape | Used by eval-case |
|---|---|---|
| `input.canonical/` | Refs to 04_synthesize + 03_analyze + 02_extract v1.json | F1 |
| `input.missing-synth.txt` | "no 04_synthesize/v1.json" | F2 |
| `expected_v1.json` | The formatted JSON | F1 |
| `expected_v1.md` | The formatted Markdown | F1 |
| `expected_meta.json` | Canonical meta + finalize-eligible | F1 |
