# Fixtures for 02-extract

| File | Shape | Used by eval-case |
|---|---|---|
| `input.canonical.txt` | Path to _shared/fixtures/qec-input.txt | E1 |
| `input.empty.txt` | Empty string | E2 |
| `input.huge.txt` | Truncate-at-50K marker | E3 |
| `expected_option_A.json` | entity-first shape | E1 |
| `expected_option_B.json` | fact-first shape | E1 |
| `expected_option_C.json` | quote-first shape | E1 |
| `expected_winner.json` | The single-winner variant from smoke | E1 (smoke reference) |
