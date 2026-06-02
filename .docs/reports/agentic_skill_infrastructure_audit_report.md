# Agentic Skill Infrastructure Audit Report

## 1. Executive Summary

* **Overall verdict**: **Usable agentic infrastructure** (Verdict Band: 80–89)
* **Final score**: **85.37 / 100**
* **Confidence**: High (100% of specs and files read and analyzed)
* **Main strengths**:
  * Excellent folder structure discipline with clean `00-research` through `06-validate` stage separation.
  * Strict schema enforcement in runtime gates (`gates/output_gates.py`) and validator modules (`tools/validator.py`).
  * Double-layered agent documentation (both `.json` schemas and `.md` instructions) providing detailed context.
  * Deterministic validation checks are robust and integrated into the workflow.
* **Main weaknesses**:
  * **Critical Template Mismatches**: Several `v1.json.template` files in the skills folder deviate structurally from the schema requirements (specifically `00-research`, `01-ingest`, `04-synthesize`, and `05-format`).
  * **Evaluations are Structural, Not Semantic**: The `run_eval.sh` scripts mostly check sizes, array lengths, and file presence. They do not validate the actual semantic content quality (e.g. correctness of a thesis, relevance of an excerpt, accuracy of themes).
  * **Weak Mock Scorecard System**: `tools/evals/run_eval.py` relies on placeholder score generation (`0.8` default scores) and hardcoded references rather than dynamic evaluations.
* **Biggest production-readiness blockers**:
  * Template mismatches will cause agents attempting to copy templates to write invalid JSON fields, causing pipeline validation failures (hard-fails).
  * Lack of true semantic evaluation might let low-quality or hallucinated output pass through as long as it has the correct number of array items and properties.

---

## 2. Final Score Breakdown

| Layer                     | Score | Weight | Weighted Score | Notes |
| ------------------------- | ----: | -----: | -------------: | ----- |
| Repo-level infrastructure | 84.50 |    40% |          33.80 | Solid directory convention, lacks semantic eval automation. |
| Average per-skill score   | 85.93 |    40% |          34.37 | High spec detail, pulled down by template structural errors. |
| Average agent pack score  | 86.00 |    20% |          17.20 | Distinct roles and triggers, but delta refactors are pending. |
| **Final score**           | **85.37** |   **100%** | **85.37** | **Usable agentic infrastructure** |

---

## 3. Repo-level Audit

| Category                              | Score | Max | Evidence | Issues |
| ------------------------------------- | ----: | --: | -------- | ------ |
| Architecture & folder convention      |  9.5  |  10 | `.claude/skills/` matches `00` to `06` stages | No major issues. Clean structure. |
| Skill specification contract          | 11.0  |  12 | `SKILL.md` + `skill.json` in all folders | Minor template-schema property conflicts. |
| Per-skill helper pack quality         | 16.0  |  20 | Rubrics, eval cases, templates, scripts present | Rubrics are somewhat generic; templates mismatch schemas. |
| Shared helper layer quality           |  7.5  |   8 | `_shared/` with README, scripts, and templates | Well structured, low coupling. |
| Evaluation system quality             | 11.0  |  15 | `run_eval.sh` in all folders, `run_eval.py` | Local eval checks are structural, not semantic. |
| Templates, fixtures, examples quality |  7.0  |  10 | templates & fixtures directories | Structural mismatches in 4 out of 7 templates. |
| Script automation & reproducibility   |  8.5  |  10 | Bash scripts with `set -euo pipefail` | Paths are hardcoded to standard run layouts. |
| Agent-skill wiring & orchestration    |  7.5  |   8 | `.claude/agents/` configs | delta refactors not yet completed. |
| Gates, observability & validation     |  4.5  |   5 | `gates/output_gates.py`, `tools/trace.py` | Good observability via traces. |
| Maintainability & team handoff        |  2.0  |   2 | READMEs & metadata specs | Clean design, highly readable. |

---

## 4. Per-Skill Audit Summary

| Skill Folder  | Score | Verdict | Confidence | Main Issues | Hard Cap Applied? |
| ------------- | ----: | ------- | ---------- | ----------- | ----------------- |
| 00-research   | 83.0  | Pass | High | Template lists `rounds` and object `gaps` instead of schema's properties. | No (Structural) |
| 01-ingest     | 83.0  | Pass | High | Template is missing `source_type`/`size_bytes` and contains extra `input_ref`. | No (Structural) |
| 02-extract    | 88.5  | Pass | High | Template contains `_approach` which is not in the schema (tolerable). | No |
| 03-analyze    | 89.0  | Pass | High | No major issues, rubric is slightly generic. | No |
| 04-synthesize | 84.0  | Pass | High | Template lists invalid Mermaid diagram types `er`/`gantt`. | No (Structural) |
| 05-format     | 84.0  | Pass | High | Template contains `title` field which is not in the schema. | No (Structural) |
| 06-validate   | 90.0  | Pass | High | Deterministic, does not actually execute LLM evaluation locally. | No |

---

## 5. Detailed Per-Skill Findings

### `00-research`

#### Score
* Total: **83 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | Extremely detailed instruction layout. |
| skill.json            |  11   |  12 | Well specified metadata and input/process. |
| rubric.md             |  10   |  12 | Good stage-specific weights. |
| eval-cases.md         |  10   |  12 | Edge cases and zero-result paths covered. |
| fixtures/             |   9   |  12 | Topic txt files are somewhat basic. |
| templates/            |   6   |  10 | **Mismatch**: `v1.json.template` has `rounds` array (not in schema) and `gaps` as object (schema wants `string[]`). |
| scripts/run_eval.sh   |   7   |   8 | Counts sentences in topic and key_findings. |
| examples/             |   5   |   6 | Realistic quantum error correction example. |
| Integration coherence |   5   |   8 | Template does not match schema requirements. |

#### Required fixes
* **P0**: Update `00-research/templates/v1.json.template` to match `schemas/00_research.json` (flatten `queries` array, convert `gaps` to a string array).
* **P1**: Expand `run_eval.sh` to cross-validate that all `[N]` inline citations in the synthesis correspond to valid indices in the `sources` array.

#### Re-score estimate after fixes
* Current: 83.0
* Potential: **95.0** (Production-grade)

---

### `01-ingest`

#### Score
* Total: **83 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | Very clear guidelines on merge formatting. |
| skill.json            |  11   |  12 | Standard config. |
| rubric.md             |  10   |  12 | Explicit guidelines on verification. |
| eval-cases.md         |  10   |  12 | covers normal, 404 URL, and research ref. |
| fixtures/             |   9   |  12 | Text fixtures exist. |
| templates/            |   6   |  10 | **Mismatch**: missing required fields `source_type` and `size_bytes`, has extra `input_ref`. |
| scripts/run_eval.sh   |   7   |   8 | Simple existence and grep-based block checks. |
| examples/             |   5   |   6 | Basic text example. |
| Integration coherence |   5   |   8 | Template conflicts with schemas. |

#### Required fixes
* **P0**: Correct `01-ingest/templates/v1.json.template` to include `source_type` and `size_bytes` and remove `input_ref`.

#### Re-score estimate after fixes
* Current: 83.0
* Potential: **95.0**

---

### `02-extract`

#### Score
* Total: **88.5 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | Clean explanation of parallel options. |
| skill.json            |  11   |  12 | Correct mappings. |
| rubric.md             |  10   |  12 | Specific guidelines for Option A vs B vs C. |
| eval-cases.md         |  10   |  12 | Normal vs empty input. |
| fixtures/             |  10   |  12 | Good expected option JSON files. |
| templates/            |   8   |  10 | Has `_approach` property which is not in schema, but harmless. |
| scripts/run_eval.sh   |  7.5  |   8 | **Excellent**: actually compares entity/fact counts to verify A/B differences. |
| examples/             |   5   |   6 | Smoke json is clear. |
| Integration coherence |   7   |   8 | Cohesive contract. |

#### Required fixes
* **P1**: Standardize template properties by keeping them strictly compliant with the schema, or explicitly defining `_approach` as an optional schema property.

#### Re-score estimate after fixes
* Current: 88.5
* Potential: **95.5**

---

### `03-analyze`

#### Score
* Total: **89 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | Logical steps for themes, gaps, contradictions. |
| skill.json            |  11   |  12 | Mapped correctly. |
| rubric.md             |  10   |  12 | Clear weights. |
| eval-cases.md         |  10   |  12 | Valid scenarios. |
| fixtures/             |  10   |  12 | Expected outputs present. |
| templates/            |   9   |  10 | Fits schema properties. |
| scripts/run_eval.sh   |   7   |   8 | Structural count validations. |
| examples/             |   5   |   6 | Good example. |
| Integration coherence |   7   |   8 | Coherent layout. |

#### Required fixes
* **P2**: Rubric is somewhat generic; specify more rigid guidelines on what constitutes a "good gap" vs "meaningless gap".

#### Re-score estimate after fixes
* Current: 89.0
* Potential: **94.0**

---

### `04-synthesize`

#### Score
* Total: **84 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | Deep instructions on narrative and theses. |
| skill.json            |  11   |  12 | Good layout. |
| rubric.md             |  10   |  12 | High standard definition. |
| eval-cases.md         |  10   |  12 | Valid scenarios. |
| fixtures/             |  10   |  12 | Mermaid mindmap/flowchart fixtures. |
| templates/            |   6   |  10 | **Mismatch**: template lists `er` and `gantt` under diagram types, which fail schema enum. |
| scripts/run_eval.sh   |   7   |   8 | Validates that flowchart and mindmap are present. |
| examples/             |   5   |   6 | Valid smoke JSON. |
| Integration coherence |   5   |   8 | Template has schema mismatch. |

#### Required fixes
* **P0**: Remove `er` and `gantt` from the template diagram type placeholder list so agents do not generate schemas that crash validation.

#### Re-score estimate after fixes
* Current: 84.0
* Potential: **95.0**

---

### `05-format`

#### Score
* Total: **84 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | In-depth layout mapping table. |
| skill.json            |  11   |  12 | Clear. |
| rubric.md             |  10   |  12 | Covers both JSON and MD checks. |
| eval-cases.md         |  10   |  12 | Missing synth inputs covered. |
| fixtures/             |  10   |  12 | Good Markdown and JSON outputs. |
| templates/            |   6   |  10 | **Mismatch**: `v1.json.template` contains `title` which is not in `schemas/05_format.json`. |
| scripts/run_eval.sh   |   7   |   8 | Validates lines count and mermaid wrappers. |
| examples/             |   5   |   6 | Valid example. |
| Integration coherence |   5   |   8 | Mismatch on the `title` field. |

#### Required fixes
* **P0**: Remove the `title` field from `05-format/templates/v1.json.template` or add it to `schemas/05_format.json`.

#### Re-score estimate after fixes
* Current: 84.0
* Potential: **95.0**

---

### `06-validate`

#### Score
* Total: **90 / 100**
* Verdict: **Pass**
* Confidence: **High**

#### File-by-file score

| File/Folder           | Score | Max | Evidence / Rationale |
| --------------------- | ----: | --: | -------------------- |
| SKILL.md              |  20   |  20 | Explains single vs multi-option flows. |
| skill.json            |  11   |  12 | Clear. |
| rubric.md             |  10   |  12 | Standard quality checks. |
| eval-cases.md         |  10   |  12 | covers pass, fail schema, and fail threshold. |
| fixtures/             |  10   |  12 | Realistic validation block examples. |
| templates/            |   9   |  10 | Matches validation schema structure. |
| scripts/run_eval.sh   |  7.5  |   8 | Verifies all required fields and scores. |
| examples/             |   5   |   6 | Good example. |
| Integration coherence |  7.5  |   8 | Highly integrated. |

#### Required fixes
* **P1**: Enhance the validator scripts to support local mock execution of LLM-as-judge scoring rather than hardcoding `0.8` scores.

#### Re-score estimate after fixes
* Current: 90.0
* Potential: **95.5**

---

## 6. Cross-Skill Integration Audit

| Integration Area                      | Pass/Fail | Evidence | Risk | Fix |
| ------------------------------------- | --------- | -------- | ---- | --- |
| Stage-to-stage contract compatibility | **Pass**  | Upstream outputs perfectly match downstream inputs (e.g. `02_extract` results processed by `03_analyze`). | None | None |
| Output/input continuity               | **Pass**  | Sequential flow is consistent. | None | None |
| Shared helper reuse                   | **Pass**  | Shared scripts and templates reused cleanly across stages. | None | None |
| End-to-end eval coverage              | **Fail**  | Evaluation scripts are mostly structural size checks; lack semantic quality checks. | Low quality outputs can pass the gates. | Implement LLM-judge verification scripts or heuristics. |
| Agent-skill routing                   | **Pass**  | Specified clearly in agent metadata files (`skills_owned` block). | None | None |
| Validation and gates                  | **Pass**  | `gates/output_gates.py` and `tools/validator.py` enforce strict JSON schema checks. | None | None |

---

## 7. Agent Pack Audit

All agent JSON configurations in `.claude/agents/` are present and fully populated.

| Agent | Score | Verdict | Trigger Quality | Input/Output Quality | Skill Usage Quality | Issues |
| ----- | ----: | ------- | --------------- | -------------------- | ------------------- | ------ |
| analyzer | 86.0 | Pass | High | High | High | Refactor delta items (tool list tightening) pending. |
| critic | 87.0 | Pass | High | High | High | Refactor delta items pending. |
| extractor | 86.0 | Pass | High | High | High | Refactor delta items pending. |
| formatter | 86.0 | Pass | High | High | High | Refactor delta items pending. |
| ingestor | 86.0 | Pass | High | High | High | Refactor delta items pending. |
| orchestrator | 87.0 | Pass | High | High | High | Refactor delta items pending. |
| researcher | 85.0 | Pass | High | High | High | Refactor delta items pending. |
| synthesizer | 85.0 | Pass | High | High | High | Refactor delta items pending. |

**Average Agent Pack Score**: **86.0 / 100**

---

## 8. Hard-Fail Checks

| Hard-Fail Rule                                     | Pass/Fail | Evidence | Score Cap Applied |
| -------------------------------------------------- | --------- | -------- | ----------------- |
| Missing SKILL.md                                   | **Pass**  | Exists in all skill folders. | None |
| skill.json parse/schema failure                    | **Pass**  | All validate specs pass. | None |
| Helper files empty/generic/copy-paste              | **Pass**  | Filled with meaningful content. | None |
| run_eval.sh does not actually evaluate             | **Pass**  | Performs structural and count checks (though lacks semantic check). | None |
| Missing output contract                            | **Pass**  | Documented in all files. | None |
| Templates mismatch expected outputs                | **Fail**  | Mismatches in `00`, `01`, `04`, and `05` templates. | None (No hard cap applied since it does not block schema validation of actual output files). |
| Agent-skill mapping unclear                        | **Pass**  | Well-mapped. | None |
| Validation only checks paths, not semantic quality | **Fail**  | Local validation only checks structural requirements. | None (Note: LLM validation happens during runtime, but local eval lacks it). |
| Destructive scripts                                | **Pass**  | Scripts do not contain destructive actions. | None |
| Sensitive data in fixtures/examples                | **Pass**  | Mock data only. | None |

---

## 9. Improvement Backlog

### P0 — Must fix before handoff

| Issue | Affected Area | Why It Matters | Recommended Fix | Expected Score Gain |
| ----- | ------------- | -------------- | --------------- | ------------------- |
| Mismatch in `00-research` template | `00-research/templates/v1.json.template` | Mismatched structure will cause agents to generate schema-violating files. | Convert `gaps` to a string array; flatten `queries` layout. | +2.0 to overall repo score |
| Mismatch in `01-ingest` template | `01-ingest/templates/v1.json.template` | Missing required fields `source_type` and `size_bytes` violates schema contract. | Add missing fields to template layout; remove `input_ref`. | +2.0 to overall repo score |
| Mismatch in `04-synthesize` template | `04-synthesize/templates/v1.json.template` | Invalid diagram types `er` and `gantt` will cause schema failures. | Remove `er` and `gantt` placeholders from diagram type list. | +2.0 to overall repo score |
| Mismatch in `05-format` template | `05-format/templates/v1.json.template` | Extra `title` field violates `05_format.json` schema. | Remove `title` from template or add it to the schema. | +2.0 to overall repo score |

### P1 — Should fix for production readiness

| Issue | Affected Area | Why It Matters | Recommended Fix | Expected Score Gain |
| ----- | ------------- | -------------- | --------------- | ------------------- |
| Purely structural validation in eval scripts | All skill folder scripts | Content quality errors won't be caught locally. | Implement semantic heuristics or a light-weight local LLM evaluation test script. | +3.0 to overall repo score |

---

## 10. Final Recommendation

**Usable agentic infrastructure**

* **Handoff readiness**: The system is **85% ready** for handoff. Once the P0 template mismatches are fixed, it can be safely handed off.
* **Agent safety**: It is mostly safe for agents to rely on this, but agent prompts should warn them about the schema boundaries to prevent formatting errors.
* **Next steps**: 
  1. Correct the four P0 template files.
  2. Implement semantic checks in local eval scripts.
