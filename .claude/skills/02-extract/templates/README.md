# Templates for 02-extract

The only multi-option stage. One template per approach (A/B/C).

| File | Purpose |
|---|---|
| `options-A.v1.json.template` | A: entity-first (maximize entity coverage) |
| `options-B.v1.json.template` | B: fact-first (maximize fact coverage) |
| `options-C.v1.json.template` | C: quote-first (maximize verbatim quotes) |

Each option is written to `outputs/<id>/02_extract/options/<A|B|C>/v1.json` with a sibling `v1.meta.json`.
The critic's `pick_winner` copies the chosen option to `outputs/<id>/02_extract/v1.json` (stage root).
