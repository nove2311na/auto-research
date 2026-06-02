# Refactor Plan — Research Pipeline

> **Goal:** Align the repo at `G:\My Drive\10_Learning\_Research\auto-research` to agentic best practices from Antonio Gulli (21 patterns) and the Claude Code book (12 chapters). This plan enumerates the gap per deliverable and the concrete refactor steps. **The runtime code is not modified by this plan** — only the docs at `.docs/agentic/` are produced.

## Per-deliverable gap

### Deliverable 1 — Agent inventory

**Current state:**
- 8 `agents/<role>/AGENT.md` files, each a runtime prompt that doubles as ad-hoc spec.
- Tool use is **implied** by code blocks and prose — no explicit allowlist.
- Only the researcher explicitly enumerates tools: `agents/researcher/AGENT.md:7` ("You are a Claude session with the `WebSearch` and `WebFetch` tools").
- `.claude/settings.json` `permissions.allow` is **global** (hcom-only) — no per-agent granularity.
- Identity / capabilities / state / communication fields are scattered across sections of each `AGENT.md`.

**Target state:**
- 8 formal specs in `.docs/agentic/agents/` with explicit sections: Identity, Capabilities, Constraints, State, Communication, Tool allowlist (current vs target least-privilege), Self-verification, Refactor delta.
- A proposed tightened allowlist per role (least-privilege).
- Cross-links to the skills each agent owns.

**Concrete refactor steps:**

1. **Small.** Trim each `agents/<role>/AGENT.md` to runtime essentials (the handoff instructions, the hcom templates, the hard rules). Move prose specs to `.docs/agentic/agents/0N-<role>.md`.
2. **Medium.** Propose a least-privilege allowlist per role based on the docs. Review with the team; reject over-broad permissions (e.g. researcher does not need `Edit` of `prd.json`).
3. **Large.** Implement per-agent `agents/<role>/settings.json` with `permissions.allow` so Claude Code enforces the allowlist at runtime. This is the proper "Permission Architecture" pattern from Claude Code book Ch. 2.
4. **Small.** Add the "tool allowlist current vs target" comparison table to each agent spec, then close the gap step-by-step.

---

### Deliverable 2 — Skill catalog

**Current state:**
- 6 stage skills + 1 critic/validate skill, scattered across 8 `agents/<role>/AGENT.md` files and 7 `schemas/*.json` files.
- Process steps are numbered in each `AGENT.md` (e.g. researcher has 12 steps, ingestor has ~6).
- Output schemas live in `schemas/` but the per-field template is **not** inlined in any `AGENT.md` (except the formatter's Markdown template at `agents/formatter/AGENT.md:33-88`).
- Examples exist only in `scripts/smoke_v2.py` (Python literals, not doc-friendly).
- **No agent has a numbered pre-submit self-check list.** The closest equivalents are the prose "Quality bar" + "Failure modes" sections.

**Target state:**
- 7 formal specs in `.docs/agentic/skills/` (6 stage skills + 1 `06-validate.md` for the critic's skill).
- Each spec has: Identity, Input schema, Process (with deterministic vs LLM-decided markers), Output schema (artifact template), Example (lifted from `scripts/smoke_v2.py` where possible), Self-check checklist (numbered, pre-submit), Validation, Refactor delta.
- Mermaid example in the `04_synthesize` spec (1 flowchart + 1 mindmap).
- The `02_extract` spec documents the 3-option (A/B/C) pattern with the critic's `pick_winner` semantics.
- The `04_synthesize` spec documents the `≥2 diagrams + ≥2 theses` rule.

**Concrete refactor steps:**

1. **Small.** Promote the "Quality bar" + "Failure modes" sections of each `agents/<role>/AGENT.md` into a numbered self-check checklist in the corresponding `skills/NN-<name>.md`. Cite the source.
2. **Small.** Lift the Mermaid examples from `scripts/smoke_v2.py:115-121` into `skills/04-synthesize.md`. Document the no-`mermaid`-wrapper rule (`scripts/smoke_v2.py:173`).
3. **Medium.** Add `minItems` constraints to `schemas/04_synthesize.json` for `diagrams` (≥2) and `theses` (≥2). Currently the rule lives only in the prompt (`agents/synthesizer/AGENT.md:53-54`), not in the schema — which means a 1-diagram artifact would pass `schema_check` and `completeness_check` but fail the LLM-judge. Making it schema-enforced is more deterministic.
4. **Small.** Add `minItems` to `schemas/00_research.json` for `key_findings` (≥3) and `gaps` (≤3) per the prose rule in `agents/researcher/AGENT.md:50-53`.
5. **Medium.** Author the `06-validate.md` spec for the critic's skill. Currently the critic's process is described in `agents/critic/AGENT.md` (3-checks table at L52-59). Promote this to a first-class skill.
6. **Large.** Replace the per-stage handoff prose in `agents/orchestrator/AGENT.md:44-82` with references to the new `skills/NN-*.md` files. Reduces duplication.

---

### Deliverable 3 — Validation inventory

**Current state:**
- 3 deterministic checks (schema, completeness, meta) in `tools/validator.py` + `tools/manifest.py`.
- 1 LLM-judge check, score provided by the critic (not implemented as a script — `tools/validator.py:128-137` records it).
- 2 smoke tests: `scripts/smoke_v2.py` (full 6-stage E2E) and `scripts/smoke_validator.py` (focused validator).
- 3 CLI entry points: `python -m tools.validator`, `python -m tools.manifest`, `python -m tools.artifact_io`.

**Gaps (documented in `validation/drift-detection.md`):**

- **No per-stage "completeness" beyond JSON schema `required` field check.** Per-stage rules like "≥2 diagrams" or "≥2 theses" live only in prompts.
- **No per-stage CLI driver** like `python -m tools.validate_stage 02_extract <input_id>`. Operators must pass stage+version args.
- **No automatic retry-on-fail driver.** The orchestrator's retry loop is described in `agents/orchestrator/AGENT.md:34-37` but is not implemented as a reusable script.
- **No `make` / `tox` / `pytest` setup** (`pyproject.toml` declares no test config; smoke tests run via `python scripts/smoke_*.py`).
- **No drift detection.** A run can be "incomplete" in many ways (missing meta, manifest not finalized, etc.) and the only diagnostic is `scripts/status.sh` (lists winner counts, not validation-status counts).
- **No eval rubric.** LLM-judge is the critic's own judgment; no shared rubric across runs.

**Target state:**
- 5 formal specs in `.docs/agentic/validation/`:
  1. `01-pre-execution-schema.md` — input-side schema check (currently absent; only post-execution exists).
  2. `02-post-execution-completeness.md` — current `tools/validator.py:completeness_check`.
  3. `03-llm-judge.md` — current `tools/validator.py:validate_artifact`'s LLM-judge path.
  4. `04-smoke-tests.md` — `scripts/smoke_v2.py` + `scripts/smoke_validator.py`.
  5. `05-drift-detection.md` — new surface; covers manifest, meta, stage-folder consistency.

**Concrete refactor steps:**

1. **Small.** Author the 5 validation specs (this deliverable).
2. **Medium.** Implement `tools/drift_detector.py` with sub-commands: `check-manifest`, `check-metas`, `check-stages`, `check-paths`. Read-only by default; `--fix` mode writes back. Source of truth for `validation/05-drift-detection.md`.
3. **Medium.** Implement `tools/validate_stage.py` as a per-stage driver: `python -m tools.validate_stage <input_id> <stage>` → finds latest version, runs `validate_artifact` with no LLM-judge score. Source of truth for `validation/01-pre-execution-schema.md` and `02-post-execution-completeness.md`.
4. **Large.** Author an eval rubric (a JSON file or a prompt) for the critic's LLM-judge. Score dimensions: schema adherence, completeness, factual grounding (in upstream `02_extract` facts), narrative coherence (for `04_synthesize`), etc. This makes the LLM-judge reproducible across runs.
5. **Small.** Add `make test` or `tox.ini` to standardize smoke test invocation. Per `.claude/rules/python.md`, "New tools added to `tools/` must come with a smoke test that runs in <5 seconds".

---

## Scope-per-refactor summary

| Refactor step | Scope | Phase |
|---|---|---|
| Trim 8 `AGENT.md` to runtime essentials | Small | Per-agent |
| Author 8 agent specs | Small (already done in this deliverable) | Done |
| Propose tightened allowlist per role | Medium | Per-agent |
| Implement per-agent `settings.json` | Large | Per-agent |
| Promote quality-bar / failure-modes to numbered checklist | Small | Per-skill |
| Add Mermaid examples to `04_synthesize` spec | Small | Per-skill |
| Add `minItems` to `04_synthesize` (diagrams, theses) | Medium | Schema |
| Add `minItems` to `00_research` (key_findings, gaps) | Small | Schema |
| Author `06-validate.md` critic-skill spec | Small | Per-skill |
| Replace orchestrator handoff prose with skill cross-refs | Medium | Orchestrator |
| Author 5 validation specs | Small (already done in this deliverable) | Done |
| Implement `tools/drift_detector.py` | Medium | Validation |
| Implement `tools/validate_stage.py` | Medium | Validation |
| Author eval rubric for LLM-judge | Large | Validation |
| Add `make test` / `tox.ini` | Small | Repo hygiene |
| Fix 7-vs-8 / 5-vs-6 / 5-vs-6 drift | Small | Repo hygiene |

## Phased execution order

If/when the refactor is executed (separate plan), the recommended order is:

1. **Phase A — Repo hygiene (Small):** fix the drift items (7→8, 5→6, 5→6). Update `tools/__init__.py`, `pyproject.toml`, `scripts/kickoff.sh`, `.claude/rules/python.md`, `agents/README.md`.
2. **Phase B — Schema tightening (Small/Medium):** add `minItems` to `schemas/00_research.json` and `schemas/04_synthesize.json`. Update the schemas, then update the agent prompts to remove the duplicated prose rules.
3. **Phase C — Doc consolidation (Small/Medium):** trim `agents/orchestrator/AGENT.md` handoff prose to cross-refs. Promote quality-bar / failure-modes to checklists in the new `skills/*.md`.
4. **Phase D — Validation tools (Medium):** implement `tools/drift_detector.py` + `tools/validate_stage.py`. Add `make test`.
5. **Phase E — Per-agent settings (Large):** implement per-agent `settings.json` to enforce the allowlists proposed in the new agent specs.
6. **Phase F — Eval rubric (Large):** author the LLM-judge rubric. Validate across 5+ historical runs.

## Verification of the refactor

When the refactor is executed, the success criteria are:

- [ ] `scripts/smoke_v2.py` still passes (no behavior regression)
- [ ] `scripts/smoke_validator.py` still passes
- [ ] New `scripts/smoke_drift.py` (added in Phase D) passes on historical runs
- [ ] Per-agent `settings.json` rejects denied tool calls (manual probe)
- [ ] Critic's LLM-judge scores are reproducible across 5 runs of the same input (variance < 0.1)
- [ ] All 8 `AGENT.md` runtime prompts are < 100 lines (currently some are 100+)
- [ ] No drift: 8 agents, 6 stages, 6 hard invariants, consistent across all docs
- [ ] All Mermaid examples in `04_synthesize` artifacts render correctly in the rendered `05_format/v1.md`

## Out of scope of this refactor plan

- **Implementing the refactor itself.** This plan only describes it.
- **Multi-language research** (Gulli Ch. 14 RAG in other languages) — V2.
- **Cross-input correlation** — V2.
- **Persistent memory** (Gulli Ch. 8) — V2.
- **MCP integration** (Gulli Ch. 10) — V2, but flagged in `patterns-applied.md` as a future opportunity.
- **A2A protocol** (Gulli Ch. 15) — hcom is the current substitute.
- **UI layer** — V2.
- **Per-input custom schemas** — V2.
- **Auto-archival of `outputs/`** — V2.
