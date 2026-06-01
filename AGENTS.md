# AGENTS.md — Team Memory

> Read this file at the start of every session. Hard cap 200 lines. Archive older sections to `learnings.archive/AGENTS-YYYY-MM-DD.md`.

## What this folder is

An 8-agent research-pipeline swarm coordinated by `hcom`. One orchestrator + seven workers. Input: any content (text, URL, PDF, DOCX, batch). Output: a structured folder of versioned artifacts per input + a top-level `manifest.json` audit trail. The pipeline begins with `00_research` (web research), then proceeds through `01_ingest` → `02_extract` → `03_analyze` → `04_synthesize` → `05_format`.

The pipeline is **content → research report**, not training. The 3-file Karpathy pattern (frozen `prepare.py` + mutable `train.py` + `val_bpb` metric) is gone.

## The 6 hard invariants (NEVER break)

1. **`pipeline.json` is the source of truth.** Stages, schemas, max_retries, max_options, critic threshold — all defined here. To change the pipeline, edit `pipeline.json`, not the agent prompts.
2. **Every artifact has a sibling `.meta.json`.** `producer`, `validation.status`, `score`, `feedback`. No bare artifacts.
3. **Critic is the only validator.** Producers do not self-validate. Failures loop back through the orchestrator with feedback, not the producer's own judgment.
4. **Versioned, not overwritten.** If a stage runs twice on the same input, you get `v1` + `v2`, never silent overwrite. `pick_winner` only fills the stage-root v1 from an option, never overwrites an option.
5. **`manifest.json` is the audit trail.** Every pipeline run ends with one. A pipeline is "done" only when all 6 stages have a `winner` AND `completed_at` is set.
6. **Research stage runs first, always.** Every input goes through `00_research` before `01_ingest`. The ingestor merges the dossier into its output. The orchestrator reads depth from the `--depth` CLI flag (default `medium`) and passes it to the researcher.

## The 8 agents and their hcom tags

| Tag | Folder | Role | hcom target |
|---|---|---|---|
| `orch` | `agents/orchestrator/` | Pipeline conductor — routes work, handles retries | `@research-pipeline-claude-1` |
| `research` | `agents/researcher/` | Iterative WebSearch+WebFetch → `00_research/v1.json` | `@research-pipeline-claude-8` |
| `ingest` | `agents/ingestor/` | Normalize input → `01_ingest/v1.txt` | `@research-pipeline-claude-2` |
| `extract` | `agents/extractor/` | Entities/facts/quotes → `02_extract/options/{A,B,C}/v1.json` (multi-option) | `@research-pipeline-claude-3` |
| `analyze` | `agents/analyzer/` | Themes/gaps/contradictions → `03_analyze/v1.json` | `@research-pipeline-claude-4` |
| `synth` | `agents/synthesizer/` | TL;DR + insights + narrative → `04_synthesize/v1.json` | `@research-pipeline-claude-5` |
| `critic` | `agents/critic/` | Validate every artifact; pick winner for multi-option stages | `@research-pipeline-claude-6` |
| `format` | `agents/formatter/` | Final report JSON + Markdown → `05_format/v1.{json,md}`; finalize manifest | `@research-pipeline-claude-7` |

## Communication protocol

- Orchestrator → researcher: `hcom send @research -- --title "research: <input_id> depth=<X>" --description "..." --files schemas/00_research.json`
- Orchestrator → stage agent: `hcom send @<tag> -- --title "..." --description "..." --files <upstream-artifact>`
- Stage agent → critic: `hcom send @critic -- --title "validate: <input_id> <stage>" --description "<path>"`
- Critic → orchestrator: `hcom send @orch -- --title "verdict: <input_id> <stage>" --description "pass|fail score=N feedback=..."`
- Cross-session memory: `hcom bundle prepare --for self` at the start of any new worker session.

## File ownership

| Path | Owner | Mode |
|---|---|---|
| `pipeline.json` | HUMAN | read-only for agents |
| `AGENTS.md` / `CLAUDE.md` | HUMAN | read-only for agents |
| `prd.json` | Orchestrator | read+write (state) |
| `progress.md` | Orchestrator | append-only |
| `learnings.md` | HUMAN (initially) → all agents (append) | append-only |
| `schemas/*.json` | HUMAN | read-only for agents |
| `inputs/inbox/*` | Orchestrator (moves to processed/) | read+move |
| `inputs/processed/*` | nobody | archive (gitignored) |
| `outputs/<id>/<stage>/v<N>.*` | the stage's agent | write during their turn |
| `outputs/<id>/00_research/v<N>.*` | researcher | write during their turn |
| `outputs/<id>/<stage>/v<N>.meta.json` | producer (initial) → critic (validation) | write |
| `outputs/<id>/00_research/v<N>.meta.json` | producer (initial) → critic (validation) | write |
| `outputs/<id>/<stage>/options/<X>/v1.*` | extractor | write |
| `outputs/<id>/manifest.json` | critic (via tools.manifest.record_attempt) + formatter (via tools.manifest.finalize) | write |
| `tools/artifact_io.py`, `tools/validator.py`, `tools/fetch_input.py`, `tools/manifest.py` | nobody (shared) | read+import |

## The 6 stages (from `pipeline.json`)

| Stage | Agent | Schema | Output format | Max options |
|---|---|---|---|---|
| `00_research` | researcher | `schemas/00_research.json` | `json` | 1 |
| `01_ingest` | ingestor | `schemas/01_ingest.json` | `txt` (+ optional `json`) | 1 |
| `02_extract` | extractor | `schemas/02_extract.json` | `json` (one per option, in `options/A/`, `B/`, ...) | 3 |
| `03_analyze` | analyzer | `schemas/03_analyze.json` | `json` | 1 |
| `04_synthesize` | synthesizer | `schemas/04_synthesize.json` | `json` | 1 |
| `05_format` | formatter | `schemas/05_format.json` | `json` + `md` | 1 |

## Quick commands

```bash
HCOM_DIR="$PWD/.hcom" hcom                       # TUI dashboard
HCOM_DIR="$PWD/.hcom" hcom list -v               # who's doing what
HCOM_DIR="$PWD/.hcom" hcom events --last 20      # recent activity
HCOM_DIR="$PWD/.hcom" hcom bundle prepare --for self   # what should I read first?
cat outputs/<input_id>/manifest.json             # pipeline state for one input
cat outputs/<input_id>/05_format/v1.md           # final report
python3 -m tools.artifact_io list <input_id> 03_analyze   # list versions of one stage
./scripts/run_pipeline.sh --depth deep <input_ref>    # kick off with explicit research depth
```

## Hard rules

- **Never pause to ask the human.** Loop runs indefinitely. Re-read this file + `learnings.md` if stuck.
- **Never edit another agent's artifact.** Each agent owns its stage folder.
- **Never self-validate.** The critic is the only validator.
- **Never overwrite.** Always version: v2, v3, ...
- **Never write a bare artifact.** Every `v1.json` has a sibling `v1.meta.json`.

## Reference repos the agent team can pull from (for inspiration on extraction / analysis prompts)

- `anthropics/prompt-eng-interactive-game` — prompt patterns for structured output
- `guidance-ai/guidance` — constrained decoding patterns
- `lm-sys/FastChat` — multi-agent LLM orchestration ideas
- `snarktank/ralph` — canonical Ralph Wiggum loop (state on disk)
