# research-pipeline

An 8-agent AI pipeline that takes any content (text, URL, PDF, DOCX, or a folder of them) and turns it into a structured research report. Like n8n's AI-agent node + output parser, but materialized as a folder of versioned artifacts with a full audit trail.

The swarm is coordinated by [`hcom`](https://github.com/aannoo/hcom) — one Claude per agent, all working off the same shared filesystem.

## Quick start on this Windows repo

```cmd
cd /d G:\My Drive\10_Learning\_Research\auto-research
python scripts\launch.py
python scripts\status.py
python scripts\run_pipeline.py --depth medium "Quantum error correction 2026"
```

The scripts set the repo-local `HCOM_DIR` and reclaim the `bigboss` sender identity automatically. See the full runbook at [`.docs/runbooks/pipeline_start_guide.md`](.docs/runbooks/pipeline_start_guide.md).

## The pipeline (6 stages)

```
inputs/inbox/*  →  00_research →  01_ingest  →  02_extract  →  03_analyze  →  04_synthesize  →  05_format  →  outputs/<id>/
                                  ↓             ↓              ↓              ↓                ↓
                                  └────── critic validates each stage (writes meta, retries on fail) ──────┘
```

| Stage | Agent | Skill | Output |
|---|---|---|---|
| `00_research` | researcher | WebSearch + WebFetch → dossier (always runs first; depth from `--depth` CLI flag) | `v1.json` |
| `01_ingest` | ingestor | URL/PDF/DOCX/text → plain text (merges dossier from research) | `v1.txt` (+ optional `v1.json` with metadata) |
| `02_extract` | extractor | entities, facts, quotes (up to 3 different approaches) | `options/{A,B,C}/v1.json` |
| `03_analyze` | analyzer | themes, gaps, contradictions | `v1.json` |
| `04_synthesize` | synthesizer | TL;DR, insights, narrative | `v1.json` |
| `05_format` | formatter | research-report template | `v1.json` (machine) + `v1.md` (human) |

After each stage, the **critic** runs `tools.validator.validate_artifact` — schema + completeness + (optional) LLM-as-judge. On fail, the orchestrator retries the stage agent with feedback. On max-retries-exhausted, the pipeline halts for that input.

## The 8 agents

| # | Tag | Runtime spec | hcom target |
|---|---|---|---|
| 1 | `orch` | `.claude/agents/orchestrator.{md,json}` | `@research-pipeline-claude-1` |
| 2 | `research` | `.claude/agents/researcher.{md,json}` | `@research-pipeline-claude-8` |
| 3 | `ingest` | `.claude/agents/ingestor.{md,json}` | `@research-pipeline-claude-2` |
| 4 | `extract` | `.claude/agents/extractor.{md,json}` | `@research-pipeline-claude-3` |
| 5 | `analyze` | `.claude/agents/analyzer.{md,json}` | `@research-pipeline-claude-4` |
| 6 | `synth` | `.claude/agents/synthesizer.{md,json}` | `@research-pipeline-claude-5` |
| 7 | `critic` | `.claude/agents/critic.{md,json}` | `@research-pipeline-claude-6` |
| 8 | `format` | `.claude/agents/formatter.{md,json}` | `@research-pipeline-claude-7` |

## File map

```
~/autoresearch-agentic-folder/
├── pipeline.json                   # single source of truth: stages, schemas, retries
├── AGENTS.md / CLAUDE.md           # team memory and project instructions
├── prd.json                        # pipeline state (gitignored)
├── progress.md                     # append-only audit log
├── learnings.md                    # team knowledge base
├── schemas/                        # JSON schemas (the "output parser" library)
├── inputs/{inbox,processed}/       # content to research
├── outputs/<id>/                   # one folder per input
│   ├── 01_ingest/v1.txt + v1.meta.json
│   ├── 02_extract/options/{A,B,C}/v1.json + v1.meta.json
│   ├── 02_extract/v1.json         # critic's winner
│   ├── 03_analyze/v1.json + v1.meta.json
│   ├── 04_synthesize/v1.json + v1.meta.json
│   ├── 05_format/v1.json + v1.md + v1.meta.json
│   └── manifest.json               # audit trail for this input
├── src/research_pipeline/          # importable Python implementation
│   ├── paths.py                    # canonical repo/runtime paths
│   ├── tools/                      # artifact I/O, manifest, validator, hcom helpers
│   ├── gates/                      # rule-based validation gates
│   └── cli/                        # implementations behind scripts/*.py
├── tools/                          # compatibility shims for python -m tools.*
├── gates/                          # compatibility shims + gate docs
├── scripts/                        # stable launch/run wrappers
├── .claude/
│   ├── agents/                     # 8 runtime agent specs
│   ├── skills/                     # stage skills, fixtures, templates, rubrics
│   └── settings.json               # Claude/hcom hooks and permissions
├── .docs/
│   ├── runbooks/                   # user-facing operating guides
│   ├── agentic/                    # canonical agent/skill design specs
│   ├── version/                    # versioned change notes
│   ├── reports/                    # audit reports
│   ├── plans/                      # design proposals
│   └── source/                     # external papers and upstream references
├── evals/                          # golden tasks, rubrics, scorecards
└── observability/                  # trace schemas and dashboards
```

The root `scripts/`, `tools/`, and `gates/` folders are kept intentionally as compatibility surfaces. New Python implementation should go under `src/research_pipeline/`.

## The 5 hard invariants

1. **`pipeline.json` is the source of truth.** To change the pipeline, edit it — not the agent prompts.
2. **Every artifact has a sibling `.meta.json`.** Producer + critic both write to it.
3. **Critic is the only validator.** Producers do not self-validate.
4. **Versioned, not overwritten.** v1, v2, v3 — never silent overwrite.
5. **`manifest.json` is the audit trail.** Required for a pipeline to be "done".

## How the artifact versioning works

```
outputs/<id>/02_extract/        # multi-option stage
  options/
    A/v1.json
    A/v1.meta.json
    B/v1.json
    B/v1.meta.json
    C/v1.json
    C/v1.meta.json
  v1.json                        # critic's winner (copy of options/<X>/v1.json)
  v1.meta.json                   # has picked_option, picked_score
```

```
outputs/<id>/03_analyze/        # linear stage
  v1.json
  v1.meta.json                   # validation: pass, score: 0.82, feedback: ...
  v2.json                        # if retry
  v2.meta.json                   # validation: pass, score: 0.88, ...
```

Every `v1.meta.json` looks like:
```json
{
  "version": 1,
  "stage": "02_extract",
  "input_id": "abc12345",
  "producer": "extractor",
  "produced_at": "2026-06-01T12:34:56Z",
  "parent_ref": "01_ingest/v1.txt",
  "schema_version": "1.0",
  "validation": {
    "status": "pass",
    "validator": "critic",
    "validated_at": "2026-06-01T12:35:10Z",
    "score": 0.85,
    "feedback": "all checks passed",
    "checks": {"schema": "pass", "completeness": "pass", "llm_judge": "pass"}
  }
}
```

## Adding a new pipeline stage

1. Add the stage to `pipeline.json` (id, agent, schema, max_retries, max_options).
2. Create `schemas/<NN>_<name>.json`.
3. Create `.claude/agents/<role>.md` and `.claude/agents/<role>.json` describing the agent.
4. Update `AGENTS.md` file-ownership table to list the new paths.
5. Run `./scripts/status.sh` to verify.

The orchestrator reads `pipeline.json` at runtime; no other code change is needed.

## Retargeting for a different task

To use this for something other than content research (e.g., log analysis, code review, customer-feedback triage), edit:

- `pipeline.json` — change `stages[].agent` and `schemas/*` to point at your new task
- Each `.claude/agents/<role>.md` and `.claude/skills/<stage>/` — rewrite the role and skill behavior
- `schemas/*.json` — replace with your task's output shape

The folder structure, hcom coordination, critic loop, and artifact versioning stay the same.

## Out of scope (V1)

- Multi-language research (search arxiv/web in other languages)
- Cross-input correlation (compare insights across many inputs)
- Persistent memory across runs (knowledge base that grows over time)
- UI layer (web viewer for `outputs/`)
- Custom schemas per-input (one global schema set; per-input override is V2)
- Fine-tuned critic
- Auto-archival of old `outputs/` to S3/cold storage

## License

Same as upstream — see `LICENSE` if present, otherwise default to your project's standard.
