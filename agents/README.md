# 7 Agents (research pipeline)

Each agent is a self-contained folder. Cross-agent comms only via `hcom send`,
`prd.json` (state), `progress.md` (audit log), `outputs/<input_id>/*` (artifacts),
and the top-level `manifest.json`.

| # | Tag | Folder | Role |
|---|---|---|---|
| 1 | `orch` | `orchestrator/` | Pipeline conductor — routes work, handles retries |
| 2 | `ingest` | `ingestor/` | Normalize input (text/URL/PDF/DOCX) → `01_ingest/v1.txt` |
| 3 | `extract` | `extractor/` | Pull entities/facts/quotes → `02_extract/options/{A,B,C}/v1.json` (multi-option) |
| 4 | `analyze` | `analyzer/` | Themes/gaps/contradictions → `03_analyze/v1.json` |
| 5 | `synth` | `synthesizer/` | TL;DR + insights + narrative → `04_synthesize/v1.json` |
| 6 | `critic` | `critic/` | Validate every artifact; pick winner for multi-option stages |
| 7 | `format` | `formatter/` | Final report JSON + Markdown → `05_format/v1.{json,md}`; finalize manifest |

## Flow

```
inputs/inbox/* → ingestor → extractor → analyzer → synthesizer → formatter → outputs/<id>/
                       ↑         ↑           ↑            ↑              ↑
                       └──────── critic validates each stage (writes meta + retries) ────┘
```

Critic is the only validator. It runs after every stage and writes
`validation.status` to the artifact's sibling `.meta.json`. On fail, the
orchestrator retries the producer with feedback (v2, v3, ...).
