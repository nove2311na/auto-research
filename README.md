# research-pipeline

A 7-agent AI pipeline that takes any content (text, URL, PDF, DOCX, or a folder of them) and turns it into a structured research report. Like n8n's AI-agent node + output parser, but materialized as a folder of versioned artifacts with a full audit trail.

The swarm is coordinated by [`hcom`](https://github.com/aannoo/hcom) — one Claude per agent, all working off the same shared filesystem.

## 60-second onboarding

```bash
cd ~/autoresearch-agentic-folder
uv sync
HCOM_DIR="$PWD/.hcom" hcom hooks add claude    # scopes hcom hooks to this folder
HCOM_DIR="$PWD/.hcom" hcom 7 claude --tag research-pipeline

# In another terminal — drop an input and watch
echo "OpenAI was founded in December 2015 by Sam Altman, Greg Brockman, Ilya Sutskever, Wojciech Zaremba, John Schulman, and Elon Musk. The company was initially a non-profit..." > inputs/inbox/openai.txt
HCOM_DIR="$PWD/.hcom" ./scripts/run_pipeline.sh inputs/inbox/openai.txt

# Tail the work
HCOM_DIR="$PWD/.hcom" hcom                       # TUI dashboard
ls outputs/                                       # one folder per input
cat outputs/<id>/05_format/v1.md                  # final report
cat outputs/<id>/manifest.json                    # audit trail
```

## The pipeline (5 stages)

```
inputs/inbox/*  →  01_ingest  →  02_extract  →  03_analyze  →  04_synthesize  →  05_format  →  outputs/<id>/
                       ↓             ↓              ↓              ↓                ↓
                       └────── critic validates each stage (writes meta, retries on fail) ──────┘
```

| Stage | Agent | Skill | Output |
|---|---|---|---|
| `01_ingest` | ingestor | URL/PDF/DOCX/text → plain text | `v1.txt` (+ optional `v1.json` with metadata) |
| `02_extract` | extractor | entities, facts, quotes (up to 3 different approaches) | `options/{A,B,C}/v1.json` |
| `03_analyze` | analyzer | themes, gaps, contradictions | `v1.json` |
| `04_synthesize` | synthesizer | TL;DR, insights, narrative | `v1.json` |
| `05_format` | formatter | research-report template | `v1.json` (machine) + `v1.md` (human) |

After each stage, the **critic** runs `tools/validator.validate_artifact` — schema + completeness + (optional) LLM-as-judge. On fail, the orchestrator retries the stage agent with feedback. On max-retries-exhausted, the pipeline halts for that input.

## The 7 agents

| # | Tag | Folder | hcom target |
|---|---|---|---|
| 1 | `orch` | `agents/orchestrator/` | `@research-pipeline-claude-1` |
| 2 | `ingest` | `agents/ingestor/` | `@research-pipeline-claude-2` |
| 3 | `extract` | `agents/extractor/` | `@research-pipeline-claude-3` |
| 4 | `analyze` | `agents/analyzer/` | `@research-pipeline-claude-4` |
| 5 | `synth` | `agents/synthesizer/` | `@research-pipeline-claude-5` |
| 6 | `critic` | `agents/critic/` | `@research-pipeline-claude-6` |
| 7 | `format` | `agents/formatter/` | `@research-pipeline-claude-7` |

## File map

```
~/autoresearch-agentic-folder/
├── pipeline.json                   # single source of truth: stages, schemas, retries
├── AGENTS.md → CLAUDE.md           # team memory (read at session start)
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
├── tools/
│   ├── artifact_io.py              # read/write versioned artifacts (atomic)
│   ├── validator.py                # schema + completeness + LLM-judge
│   ├── fetch_input.py              # URL/PDF/DOCX → text
│   ├── manifest.py                 # build/read manifest.json
│   └── hcom_io.py                  # hcom wrappers
├── agents/<role>/AGENT.md          # 7 agent prompts
├── scripts/                        # launch + run helpers
└── .claude/settings.json           # hcom hooks
```

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
3. Create `agents/<role>/AGENT.md` describing the skill.
4. Update `AGENTS.md` file-ownership table to list the new paths.
5. Run `./scripts/status.sh` to verify.

The orchestrator reads `pipeline.json` at runtime; no other code change is needed.

## Retargeting for a different task

To use this for something other than content research (e.g., log analysis, code review, customer-feedback triage), edit:

- `pipeline.json` — change `stages[].agent` and `schemas/*` to point at your new task
- Each `agents/<role>/AGENT.md` — rewrite the skill
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
