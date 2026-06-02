# Validation Inventory — 5 Surfaces

This folder contains the formal spec for each of the 5 validation surfaces in the research-pipeline. See `../README.md` for the overall spec structure and `../refactor-plan.md` for the gap analysis.

## Overview

| # | Surface | Type | Triggered by | Spec |
|---|---|---|---|---|
| 1 | `pre-execution-schema` | Deterministic | Stage agent before writing its artifact (V2; currently manual) | [01-pre-execution-schema.md](01-pre-execution-schema.md) |
| 2 | `post-execution-completeness` | Deterministic | The critic, after a stage agent writes its artifact | [02-post-execution-completeness.md](02-post-execution-completeness.md) |
| 3 | `llm-judge` | LLM-decided (the critic) | The critic, after schema + completeness pass | [03-llm-judge.md](03-llm-judge.md) |
| 4 | `smoke-tests` | Deterministic (E2E simulation) | Developer / CI / pre-deploy | [04-smoke-tests.md](04-smoke-tests.md) |
| 5 | `drift-detection` | Deterministic (filesystem + manifest consistency) | Developer / CI / `scripts/status.sh` (V2; currently manual) | [05-drift-detection.md](05-drift-detection.md) |

## Per-validation-surface contents

Each spec follows the same template (see `../templates/validation-spec.md`):

1. **Identity** — surface name, type, triggered by, Antonio Gulli patterns, Claude Code book chapters
2. **Purpose** — what this checks, why it exists
3. **How it works** — algorithm + source-of-truth file with line refs
4. **Pass / fail criteria** — thresholds, retry semantics
5. **How to invoke** — CLI, from agent prompt, from smoke test
6. **Coverage** — per-stage table
7. **Failure modes** — what happens on schema file missing, etc.
8. **Refactor delta** — scope, current, target, concrete steps

## Cross-references

- **Skills** (what each validation checks): see `../skills/README.md`
- **Agents** (who triggers each validation): see `../agents/README.md`
- **Templates** (the canonical spec shapes): see `../templates/`
- **Runtime implementation** (canonical for now):
  - `../../tools/validator.py` — `validate_artifact`, `schema_check`, `completeness_check`
  - `../../tools/manifest.py` — `init_manifest`, `record_attempt`, `finalize`, `is_done`
  - `../../tools/artifact_io.py` — `pick_winner`, `write_meta`
  - `../../scripts/smoke_v2.py` — full 6-stage E2E
  - `../../scripts/smoke_validator.py` — focused validator smoke
  - `../../scripts/status.sh` — current V1 summary (V2 will call `drift_detector` for richer output)
- **Source of truth for thresholds:** `../../pipeline.json` → `critic.llm_judge_threshold` (default 0.7)
