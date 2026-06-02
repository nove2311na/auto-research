# Validation 04 — Smoke Tests

## Identity

| Field | Value |
|---|---|
| Surface | `smoke-tests` |
| Type | Deterministic (E2E pipeline simulation) |
| Triggered by | Developer / CI / pre-deploy |
| Antonio Gulli patterns | Ch. 17 Resource-Aware Optimization, Ch. 19 Evaluation & Monitoring |
| Claude Code book chapters | Ch. 11 CI/CD & Headless Automation |

## Purpose

- **What this checks:** That the pipeline runs end-to-end with deterministic inputs, producing all 6 stage artifacts + a finalized manifest + a valid `v1.md`. Catches regressions in the validator, the manifest helper, the artifact I/O, and the schema definitions.
- **Why it exists:** Unit tests for `tools/*.py` are V2 (`AGENTS.md` / `python.md` say so). Smoke tests fill the gap: they exercise the full pipeline with simulated producer agents, so any breaking change to the schemas, the validator, or the manifest is caught.

## How it works

### Algorithm

`scripts/smoke_v2.py` simulates all 6 stage agents with hard-coded Python literals:

1. **00_research** — `research_artifact` (lines 18–45) with topic, depth, queries, sources, synthesis, key_findings, gaps.
2. **01_ingest** — `ingest_text` (lines 48–62) merges the dossier into plain text; `ingest_meta` (lines 63–71) is the JSON variant.
3. **02_extract** — `extract_winner` (lines 74–86) with entities, facts, quotes (winner variant; multi-option is implied).
4. **03_analyze** — `analyze_artifact` (lines 89–105) with themes, gaps, contradictions.
5. **04_synthesize** — `synth_artifact` (lines 108–132) with summary, insights, narrative, 2 diagrams, 2 theses.
6. **05_format** — `format_json` (lines 135–144) consolidates upstream; `render_md()` (lines 147–188) produces `v1.md`.

Then for each stage:

- Write `v1.json` + `v1.meta.json` via `tools.artifact_io`.
- Call `validate_artifact(..., llm_judge_score=0.85)` to simulate the critic.
- Call `tools.manifest.record_attempt(...)` to record the attempt.
- Print PASS/FAIL per stage.

Then 10 assertions (lines 232–286):

1. All 6 stages passed.
2. Manifest has 6 stages.
3. Every stage has `winner=v1`.
4. After `finalize`, `is_done()` returns True.
5. `v1.md` has 2 `mermaid` blocks.
6. `v1.md` has 2 thesis sections.
7. `01_ingest` merged the dossier (contains `## Research Context` + `[1]` + `[2]`).
8. `metadata.research_ref = "00_research/v1.json"`.
9. `05_format/v1.json` has 2 diagrams + 2 theses.
10. `manifest.completed_at` is filled.

### Source of truth

- `scripts/smoke_v2.py` — full E2E smoke (290 lines).
- `scripts/smoke_validator.py` — focused validator smoke (64 lines, runs in <1s).

### Inputs

- Hard-coded `INPUT_ID = "smokev200"` (or `"smoke0001"` for the validator-only smoke).
- Hard-coded `TOPIC = "Quantum error correction 2026"`.

### Outputs

- `outputs/smokev200/{00_research,01_ingest,02_extract,03_analyze,04_synthesize,05_format}/v1.{json,txt,md}` — all 6 stage artifacts.
- `outputs/smokev200/manifest.json` — the audit trail.
- Stdout: PASS/FAIL per stage + 10 assertion results.
- Exit code: 0 on all-pass, non-zero on any fail.

## Pass / fail criteria

- **Pass:** all 10 assertions succeed; all 6 stages pass `validate_artifact` with score 0.85.
- **Fail:** any assertion fails, or any stage fails `validate_artifact`.
- **Threshold:** Score 0.85 ≥ 0.7 (the LLM-judge threshold).
- **Retry semantics:** N/A — smoke tests are run-once. Failure indicates a regression to fix.

## How to invoke

### CLI

```bash
# Full 6-stage E2E
python scripts/smoke_v2.py

# Focused validator
python scripts/smoke_validator.py
```

### From CI

Planned: `.github/workflows/autoresearch.yml` V2 (per `README.md` §"Out of scope" V2).

### From a developer

Run before pushing changes to `tools/`, `schemas/`, or `agents/<role>/AGENT.md`.

## Coverage

| Layer | Smoke exercises? | Notes |
|---|---|---|
| `tools/artifact_io.py` | yes | write/read/build_meta/write_meta/pick_winner (implicit via `smoke_v2`) |
| `tools/validator.py` | yes | `validate_artifact`, `schema_check`, `completeness_check` |
| `tools/manifest.py` | yes | `init_manifest`, `record_attempt`, `finalize`, `is_done` |
| `tools/fetch_input.py` | no | (V2 — add `scripts/smoke_fetch.py`) |
| `tools/hcom_io.py` | no | (V2 — hcom is a separate CLI; not unit-testable) |
| `schemas/00_research.json` | yes | via `research_artifact` |
| `schemas/01_ingest.json` | yes | via `ingest_meta` |
| `schemas/02_extract.json` | yes | via `extract_winner` |
| `schemas/03_analyze.json` | yes | via `analyze_artifact` |
| `schemas/04_synthesize.json` | yes | via `synth_artifact` |
| `schemas/05_format.json` | yes | via `format_json` |
| `schemas/manifest.json` | yes | implicitly via `init_manifest` output |
| Mermaid rendering | yes | asserts 2 `mermaid` blocks in `v1.md` (line 256) |
| Multi-option (02_extract) | no | V2 — add a 3-option variant to `smoke_v2.py` |
| Per-stage CLI | no | V2 — `tools/validate_stage.py` |

## Failure modes

- **Schema file missing** → `jsonschema` raises; `validate_artifact` returns fail. The smoke test asserts and exits non-zero.
- **Mermaid block count != 2** → assertion 5 fails. Indicates the synthesizer's diagrams rule changed but the smoke test wasn't updated.
- **`is_done()` returns False after `finalize`** → assertion 4 fails. Indicates a regression in the manifest helper.
- **Empty `insights`/`theses`/`diagrams` arrays** → schema passes (no `minItems`), but the assertion in `smoke_v2.py:281` would catch it (via `len(fmt_on_disk["diagrams"]) == 2`).

## Refactor delta

- **Scope:** Small/Medium
- **Current state:** 2 smoke tests. `smoke_v2.py` covers the full 6-stage pipeline. `smoke_validator.py` covers the validator's 4 boundary cases.
- **Target state:** Add `make test` (or `tox.ini`) to run both. Add per-tool smokes (`smoke_fetch.py`, `smoke_artifact_io.py`). Add a multi-option variant.
- **Concrete steps:**
  1. Add `Makefile` with `test: python scripts/smoke_v2.py && python scripts/smoke_validator.py`.
  2. Add `scripts/smoke_artifact_io.py` (tests `pick_winner` with 3 options, asserts the stage-root `v1` matches the highest-scoring option).
  3. Add `scripts/smoke_fetch.py` (tests `fetch_input.fetch` with a `.txt`, a fake PDF, a fake DOCX, a URL — all offline).
  4. Add a 3-option variant to `smoke_v2.py` (build `options/A/v1.json`, `options/B/v1.json`, `options/C/v1.json` with deliberately different shapes; assert `pick_winner` picks correctly).
  5. Per `.claude/rules/python.md`: all new smokes must run in <5s and not require network or LLM access.

## Source files (for traceability)

- `scripts/smoke_v2.py` — full 6-stage E2E (290 lines)
- `scripts/smoke_validator.py` — focused validator smoke (64 lines)
- `tools/artifact_io.py` — exercised by `smoke_v2.py`
- `tools/validator.py` — exercised by both
- `tools/manifest.py` — exercised by `smoke_v2.py`
- `schemas/*.json` — all 6 exercised by `smoke_v2.py`
- `.claude/rules/python.md` — "Testing" section (smoke <5s, no network, no LLM)
