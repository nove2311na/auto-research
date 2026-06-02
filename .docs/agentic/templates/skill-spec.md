# Template — Skill Spec

> **Use this template for every `skills/NN-<name>.md` file in `.docs/agentic/skills/`.**
> Sections marked `[required]` must be present. Sections marked `[recommended]` may be omitted only with justification. Sections marked `[optional]` are at author discretion.

## Identity `[required]`

| Field | Value |
|---|---|
| Stage id | (e.g. `00_research`) |
| Owning agent | (e.g. `researcher`) |
| Schema | (e.g. `schemas/00_research.json`) |
| Output format | (e.g. `json` / `txt` / `json+md`) |
| `max_options` | (from `pipeline.json`) |
| `max_retries` | (from `pipeline.json`) |
| Antonio Gulli patterns | (Ch. 5 Tool Use, Ch. 10 MCP, Ch. 8 Memory, Ch. 12 Exception Handling, etc.) |

## Input schema `[required]`

### Fields
| Field | Type | Required | Source |
|---|---|---|---|
| (e.g. `input_id`) | `string` (8 hex) | yes | hcom message |
| (e.g. `input_ref`) | `string` (path/URL/topic) | yes | hcom message |
| (e.g. `depth`) | `enum: shallow\|medium\|deep` | yes (default `medium`) | `--depth` CLI flag |

### Example hcom message
```bash
hcom send --name <sender> "@research-pipeline-claude-N <stage>: <input_id>; input=<upstream paths>; description=..."
```

### Source
- `schemas/<NN>_<name>.json` — for the artifact contract
- `agents/<role>/AGENT.md` — for the input prose description

## Process `[required]`

Numbered steps. For each step, indicate **deterministic** vs **LLM-decided**:

1. **(deterministic)** Read upstream artifact at `<path>`.
2. **(LLM-decided)** Decide whether to merge dossier / pick option / etc.
3. **(deterministic)** Call `tools.artifact_io.write_artifact(...)`.
4. **(LLM-decided)** Compose `.meta.json` via `build_meta(...)`.
5. **(deterministic)** Ping `@critic` with `validate: <input_id> <stage>`.

For multi-option skills (e.g. `02_extract`), enumerate sub-processes for each option:

- **Option A** (`entity-first`): ...
- **Option B** (`fact-first`): ...
- **Option C** (`quote-first`): ...
- **Critic's pick:** (cite `tools.artifact_io.pick_winner` + `AGENTS.md` invariant #4)

## Output schema (artifact template) `[required]`

### Top-level required fields
- (list of `required` keys from the schema; for multi-option, the option file has the same shape as the stage-root)

### Field-by-field template
- For each required field, give a 1-line template + the schema enum if any
- E.g. for `04_synthesize.diagrams[].type`: `enum: flowchart|sequence|mindmap|graph|class|state|concept`

### Markdown example (full v1 artifact)
```json
{
  "<field_1>": "...",
  "<field_2>": [...],
  ...
}
```

For `05_format` only: also include a full `v1.md` template.

## Example `[required]`

> **Prefer a real artifact** from `scripts/smoke_v2.py`. Mark `synthetic` if you author it yourself.

### Real (lifted from `scripts/smoke_v2.py`)
```json
{lifted}
```

### Synthetic (only if no real example exists)
```json
{...}
```

For `04_synthesize`: include 1 `flowchart` + 1 `mindmap` Mermaid example verbatim.

## Self-check checklist (pre-submit, numbered) `[required]`

- [ ] **Schema:** all `required` fields present, types match schema
- [ ] **Completeness:** no null / `""` / `{}` in required fields (empty arrays OK)
- [ ] **Citations:** inline `[N]` citations resolve to `sources[]` index
- [ ] **Enums:** all enum fields use the schema-declared values
- [ ] **Diagrams:** ≥2 present, types span the required set (synthesize only)
- [ ] **Theses:** ≥2 present, `confidence` enum valid (synthesize only)
- [ ] **Meta:** sibling `v1.meta.json` written via `build_meta` + `write_meta`
- [ ] **Handoff:** `@critic` pinged with correct title pattern
- [ ] **Failure log:** if any non-fatal issue occurred, it appears in `gaps[]` (research) or `progress.md`
- (per-stage additions, e.g. "3 options are visibly different" for extract)

## Validation `[required]`

- **Which check:** (link to `validation/<surface>.md`)
- **Threshold:** (e.g. `pipeline.json` → `critic.llm_judge_threshold` = 0.7)
- **Common failure → fix:** (e.g. "schema fail on `summary.maxLength=1000` → trim to 800 chars and resubmit")

## Failure modes `[recommended]`

- (what this skill does on missing input, schema violation, retries exhausted, etc.; cite the agent's `## Failure modes` section)

## Refactor delta `[required]`

- **Scope:** (Small / Medium / Large)
- **Current state:** (1-2 sentences — where this skill's spec is currently buried)
- **Target state:** (1-2 sentences — what the post-refactor shape is)
- **Concrete steps:**
  1. ...
  2. ...

## Source files (for traceability)

- `schemas/<NN>_<name>.json` — machine contract
- `agents/<role>/AGENT.md` — runtime prompt
- `scripts/smoke_v2.py` — real example artifact
- (etc.)

---

**Authoring tips:**
- **Numbered process steps** with explicit `(deterministic)` / `(LLM-decided)` markers. The user values the distinction (see `AGENTS.md` "The pipeline is **content → research report**, not training" — i.e. some steps are pure LLM, others are pure code).
- **Lift examples from `scripts/smoke_v2.py` whenever possible** — it is the canonical "what good looks like" corpus.
- **Citation format `[N]`** for inline references to upstream `sources[]` arrays (Gulli Ch. 5 Tool Use pattern: "ground responses in retrieved evidence").
- **Mermaid diagrams** must NOT include the ```` ```mermaid ```` wrapper in the artifact's `code` field — the wrapper is added by the formatter when rendering `v1.md` (see `scripts/smoke_v2.py:173`).
