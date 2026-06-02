# Validation 05 — Drift Detection

## Identity

| Field | Value |
|---|---|
| Surface | `drift-detection` |
| Type | Deterministic (filesystem + manifest consistency) |
| Triggered by | Developer / CI / `scripts/status.sh` (currently manual; see Refactor delta) |
| Antonio Gulli patterns | Ch. 12 Exception Handling, Ch. 19 Evaluation & Monitoring |
| Claude Code book chapters | Ch. 10 Failure Modes, Ch. 11 CI/CD & Headless Automation |

## Purpose

- **What this checks:** That the **state on disk** is internally consistent — manifest matches stage folders, every artifact has a sibling meta, every winner has a corresponding file, and the schema set matches `pipeline.json`.
- **Why it exists:** The pipeline produces many files across 6 stages (and 3 options for `02_extract`). A run can be "incomplete" in many ways that the critic doesn't catch:
  - An artifact is written but no meta (producer didn't call `write_meta`).
  - A manifest has a `winner=v3` but no `v3.json` on disk.
  - `pipeline.json` references `schemas/06_something.json` that doesn't exist.
  - An input was started but never finalized (no `completed_at`).

## How it works

### Algorithm (planned for V2)

```bash
python -m tools.drift_detector <input_id> [--fix] [--check {manifest,metas,stages,paths,schemas,all}]
```

Four sub-checks:

1. **`check-manifest`**: `manifest.stages[i].winner` corresponds to an actual `v<N>.<ext>` file on disk. `completed_at` is set iff all stages have winners.
2. **`check-metas`**: every `v<N>.<ext>` in any stage folder has a sibling `v<N>.meta.json`. Every `meta.validation.status` is in `{pending, pass, fail}`.
3. **`check-stages`**: every stage id in `manifest.stages[]` exists as a subfolder. Every stage id in `pipeline.json#stages` is in the manifest. No orphan stage folders.
4. **`check-paths`**: `manifest.input_ref` exists at the recorded path. `inputs/inbox/*` does not have stale files (the orchestrator should have moved them to `processed/`).
5. **`check-schemas`** (V2.1): every `pipeline.json#stages[].schema` file exists. Every schema's `required` array matches the producer's `build_meta` defaults.

### Source of truth (planned)

- `tools/drift_detector.py` (V2) — to be authored.
- Reuses `tools/manifest.py:is_done`, `read_manifest`.
- Reuses `tools/artifact_io.py:list_versions`, `read_meta`.
- Reuses `tools/validator.py:load_schema` for the schema check.

### Inputs

- `input_id` (the run to check)
- `--check` flag (which sub-check to run; default `all`)
- `--fix` flag (V2.1: attempt auto-repair; default read-only)

### Outputs

- `{"status": "ok|drift", "checks": {<sub>: {"status": "ok|fail", "issues": [...]}}}`
- Stdout: human-readable summary

## Pass / fail criteria

- **Pass (`ok`):** all sub-checks pass; no issues found.
- **Fail (`drift`):** at least one sub-check finds an issue.
- **Threshold:** N/A (deterministic).
- **Retry semantics:** N/A — this is a diagnostic, not a gate. The orchestrator does not call it mid-pipeline. It is run by developers / CI.

## How to invoke

### CLI (planned)

```bash
# Check one input
python -m tools.drift_detector smokev200

# Check a specific sub-check
python -m tools.drift_detector smokev200 --check metas

# Auto-fix (V2.1; dangerous)
python -m tools.drift_detector smokev200 --fix
```

### From `scripts/status.sh` (V1 — manual summary)

`scripts/status.sh:42-55` lists per-input winner counts. This is a 1-line summary; full drift detection is V2.

### From CI

Planned: `.github/workflows/autoresearch.yml` V2 runs `drift_detector` on all `outputs/*` once a day.

## Coverage

| Sub-check | What it catches |
|---|---|
| `check-manifest` | winner pointing to nonexistent v<N>; manifest missing stages; `completed_at` set when not all stages have winners |
| `check-metas` | bare artifacts (no meta); meta with invalid `validation.status` enum |
| `check-stages` | stage folder missing; orphan stage folder (not in `pipeline.json`); stage id in manifest not in `pipeline.json` |
| `check-paths` | `input_ref` points to a deleted file; stale `inputs/inbox/*`; unprocessed source files |
| `check-schemas` (V2.1) | `pipeline.json` references a missing schema; schema `required` array is empty for a non-TXT stage |

## Failure modes (of the detector itself)

- **Outputs directory missing** → `FileNotFoundError`; surface verbatim. Means the run never started.
- **`manifest.json` malformed JSON** → `json.JSONDecodeError`; surface verbatim. Indicates manual corruption; do not auto-fix.
- **Permission denied** on read → surface; suggest `chmod` (the script is read-only by default).

## Refactor delta

- **Scope:** Medium
- **Current state:** No drift detector exists. The only diagnostic is `scripts/status.sh` (per-input winner counts).
- **Target state:** `tools/drift_detector.py` with 5 sub-checks. Auto-fix mode for safe repairs (e.g. re-writing a missing meta with `validation: {status: "pending"}`).
- **Concrete steps:**
  1. Author `tools/drift_detector.py` (V2).
  2. Add `scripts/smoke_drift.py` that builds 3 known-drifted outputs and asserts the detector finds all 3.
  3. Add `make drift` Makefile target.
  4. (V2.1) Add `--fix` mode with a safety check: only auto-fix issues that have a known-safe repair (e.g. missing meta with `validation: pending`).
  5. Wire `scripts/status.sh` to call `drift_detector` for richer output.

## Source files (for traceability)

- `tools/manifest.py:80-108` — `record_attempt` (sets `winner`; source of truth for `check-manifest`)
- `tools/manifest.py:118-123` — `is_done` (used by `check-manifest`)
- `tools/artifact_io.py:57-68` — `list_versions` (used by `check-stages`)
- `tools/artifact_io.py:163-167` — `read_meta` (used by `check-metas`)
- `tools/validator.py:37-43` — `load_schema` (used by `check-schemas` V2.1)
- `pipeline.json:6-61` — stage enumeration (used by `check-stages`)
- `schemas/manifest.json` — manifest schema (used by `check-manifest` V2.1)
- `scripts/status.sh:42-55` — current V1 summary
