# Skill Catalog — 7 Skills

This folder contains the formal spec for each of the 7 skills in the research-pipeline. The first 6 are pipeline stages; the 7th is the critic's cross-cutting validation skill.

See `../README.md` for the overall spec structure and `../refactor-plan.md` for the gap analysis.

## Overview

| # | Stage id | Owning agent | Schema | Spec |
|---|---|---|---|---|
| 0 | `00_research` | `researcher` | `schemas/00_research.json` | [00-research.md](00-research.md) |
| 1 | `01_ingest` | `ingestor` | `schemas/01_ingest.json` | [01-ingest.md](01-ingest.md) |
| 2 | `02_extract` | `extractor` | `schemas/02_extract.json` | [02-extract.md](02-extract.md) |
| 3 | `03_analyze` | `analyzer` | `schemas/03_analyze.json` | [03-analyze.md](03-analyze.md) |
| 4 | `04_synthesize` | `synthesizer` | `schemas/04_synthesize.json` | [04-synthesize.md](04-synthesize.md) |
| 5 | `05_format` | `formatter` | `schemas/05_format.json` | [05-format.md](05-format.md) |
| 6 | (cross-cutting) | `critic` | N/A | [06-validate.md](06-validate.md) |

## Per-skill contents

Each spec follows the same 9-section template (see `../templates/skill-spec.md`):

1. **Identity** — stage id, owning agent, schema, output format, max_options, max_retries, Antonio Gulli patterns, Claude Code book chapters
2. **Input schema** — fields, example hcom message, source
3. **Process** — numbered steps with deterministic vs LLM-decided markers
4. **Output schema (artifact template)** — top-level required fields + field-by-field template
5. **Example** — real artifact (lifted from `scripts/smoke_v2.py`) or synthetic
6. **Self-check checklist (pre-submit, numbered)** — 10-15 checks per skill
7. **Validation** — which check, threshold, common failure → fix
8. **Failure modes** — what happens on missing input, schema violation, etc.
9. **Refactor delta** — scope (S/M/L), current state, target state, concrete steps

## Cross-references

- **Agents** (who owns each skill): see `../agents/README.md`
- **Validation** (what enforces correctness): see `../validation/README.md`
- **Templates** (the canonical spec shapes): see `../templates/`
- **Source of truth for stage config:** `../../pipeline.json`
- **Runtime prompts** (where the process is currently inlined): `../../agents/<role>/AGENT.md`
- **Real example artifacts** (lifted into the specs): `../../scripts/smoke_v2.py`
