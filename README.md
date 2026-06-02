# 🤖 Auto-Research AI-Swarm Pipeline

An advanced, production-grade 8-agent AI pipeline designed to take any input content (raw text, URLs, PDFs, Word documents, or directories of them) and transform it into highly structured, peer-reviewed, and formatted research reports. 

Coordinated by [`hcom`](https://github.com/aannoo/hcom), the swarm leverages a shared filesystem to maintain state, track progress, enforce safety gates, and preserve a strict audit trail of versioned artifacts.

---

## ⚡ Quick Start (Windows PowerShell)

```powershell
# 1. Navigate to the repository root
cd "g:\My Drive\10_Learning\_Research\auto-research"

# 2. Boot up the local hcom messaging swarm TUI
python scripts\launch.py

# 3. View the swarm status dashboard & cost metrics
python scripts\status.py

# 4. Kick off a research topic with default depth
python scripts\run_pipeline.py "Quantum error correction 2026"

# 5. Run the end-to-end smoke test suite to verify pipeline integrity
$env:PYTHONPATH="src"
python -m research_pipeline.cli.smoke_v2
```

> [!TIP]
> For a detailed walkthrough on setting up and running the swarm, refer to the [Pipeline Start Guide](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/runbooks/pipeline_start_guide.md) and the [Configuration Guide](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/runbooks/configuration_guide.md).

---

## 📊 The 6-Stage Pipeline

The pipeline processes inputs sequentially, while the **Critic** acts as an independent quality guardrail verifying each output before letting the orchestrator advance:

```
inputs/inbox/*  →  00_research →  01_ingest  →  02_extract  →  03_analyze  →  04_synthesize  →  05_format  →  outputs/<id>/
                                  ↓             ↓              ↓              ↓                ↓
                                  └────── critic validates each stage (writes meta, retries on fail) ──────┘
```

| Stage | Agent | Skill Trigger | Output Artifact |
|---|---|---|---|
| `00_research` | `researcher` | Iterative WebSearch + WebFetch | `00_research/v1.json` (Topic, sources, synthesis) |
| `01_ingest` | `ingestor` | Doc parsing + Semantic Chunking | `01_ingest/v1.txt` (Merged dossier context) |
| `02_extract` | `extractor` | Parallel entities, facts & quotes extraction | `02_extract/options/{A,B,C}/v1.json` → Winner `v1.json` |
| `03_analyze` | `analyzer` | Cross-fact thematic & gap analysis | `03_analyze/v1.json` (Themes, contradictions, gaps) |
| `04_synthesize` | `synthesizer` | Insight synthesis + Mermaid charts | `04_synthesize/v1.json` (TL;DR, narrative, diagrams, theses) |
| `05_format` | `formatter` | Report templating & finalization | `05_format/v1.json` (Machine-readable) & `v1.md` (Human report) |

---

## 🌟 Swarm Features & Invariants (v1.5.0)

This swarm is optimized for token efficiency, reliability, security, and strict quality verification:

### 🔒 Swarm Security & Red-Teaming
- **Static Secret Scanning**: Automatically detects AWS credentials, GitHub PATs, Slack webhooks, and private keys in input files via `security_gates.py`.
- **Absolute Path Traversal Block**: Rejects any inputs containing directory traversal sequences (`../`, `..\\`) to prevent host directory access.
- **Input Size Hard Constraints**: Rejects inputs exceeding 2MB at the security gate to prevent Denial of Service (DoS) and context overflow.
- **Adversarial Test Suite**: Includes automated red-team cases (`evals/security-redteam/`) to validate static protections.

### ⚙️ Automated Validation Gates
- **Input Gate (`input_gates.py`)**: Probes incoming URLs using responsive HEAD/GET requests with redirects/timeouts and checks maximum input limits (5MB).
- **Implementation Gate (`implementation_gates.py`)**: Verifies that artifacts conform to version formats (`v\d+`), stage folders are generated, and upstream parent stages have winner decisions.
- **Release Gate (`release_gates.py`)**: Validates that all 6 stages have picked winners, the run is marked `completed_at`, and the formatted report (`v1.md`) is populated before releasing.

### 💡 Performance & Swarm Optimizations
- **Parallel Extraction**: Dispatches options A, B, and C concurrently during `02_extract` to separate Claude worker tags, cutting stage duration by ~60%.
- **Depth-Aware Research**: Adjusts search strategy dynamically:
  - `shallow`: 1 round, 3 queries, ≤3 sources.
  - `medium`: 2 rounds, 5 queries, ≤7 sources.
  - `deep`: 3 rounds, 5 queries, ≤15 sources.
- **Inter-run Deduplication**: Checks `outputs/` for completed manifests. Skips executing identical inputs unless the `--force` flag is specified.
- **URL Caching & Retries**: Employs global JSON response caching under `outputs/.cache/` and exponential backoff retries (3 attempts) on URL fetches.
- **Semantic Ingest Chunking**: Replaces naive 1MB truncation with keyword-density semantic chunking (40KB blocks sorted by topic relevance) when inputs exceed 1MB.
- **Self-Rebuttal Metadata**: Records Synthesizer peer reviews (`self_rebuttal_passed`, `self_rebuttal_notes`) inside `v1.meta.json`.

### 📊 Observability & Telemetry
- **Swarm Cost Dashboard**: Prints token consumption, tool use counters, and estimated USD cost directly on the `status.py` dashboard.
- **Trace Logs**: Emits stage execution performance events to `outputs/<id>/trace.jsonl`.
- **Swarm Execution Dashboard CLI**: Aggregates all JSON traces (`observability/traces/`) and performance metrics to generate ASCII summaries via:
  ```powershell
  python -m research_pipeline.tools.observability.render_dashboard <run_id>
  ```
- **Aggregate Metrics**: Log aggregate statistics (duration, token totals, tools count, average score, pass status) to `observability/aggregate_metrics.jsonl`.
- **GitHub Actions CI/CD**: Automatically installs dependencies and executes smoke test checks on push/PR events to `main`.

---

## 📁 Repository Directory Map

```
auto-research/
├── pipeline.json                   # Single source of truth: stages, schemas, budgets, and skill triggers
├── AGENTS.md / CLAUDE.md           # Team invariants, agent details, and guidelines (read-only for agents)
├── prd.json                        # Pipeline execution state (validated against schemas/prd.json)
├── progress.md                     # Append-only swarm stage transition logs
├── learnings.md                    # Cumulative swarm knowledge base (auto-updated on run success/failures)
├── schemas/                        # JSON Draft-7 schemas for stages, prd.json, and agent/skill contracts
├── inputs/                         # Inbox (incoming research requests) and Processed (archived requests)
├── outputs/<input_id>/             # Versioned outputs per run:
│   ├── 0X_stage/vN.json            # Artifact output
│   ├── 0X_stage/vN.meta.json       # Metadata containing producer, validation status, and self-rebuttal
│   ├── trace.jsonl                 # Performance telemetry events
│   ├── task_plan.md                # Living status checklist for the run
│   └── manifest.json               # Canonical audit trail with winner picks
├── src/research_pipeline/          # Core package code:
│   ├── paths.py                    # Repository path mappings
│   ├── tools/                      # Core tools (artifact_io, fetch_input, manifest, memory_retriever, validator)
│   ├── gates/                      # Gate rule definitions (input, security, implementation, release, output)
│   └── cli/                        # Swarm terminal commands (run_pipeline, status, smoke_v2, validate_specs)
├── tools/ & gates/ & scripts/      # Root compatibility shims forwarding calls to src/research_pipeline/
├── evals/                          # Evals suite (golden tasks, rubric, scorecards, security red-team files)
└── observability/                  # Audit log schemas, aggregate metrics, and dashboards
```

---

## 🛠 Invariants & Team Memory

Every agent in the swarm must adhere strictly to these invariants:
1. **`pipeline.json` is the sole source of truth**: Stages, budgets, schemas, and retries are defined here.
2. **Every artifact has a sibling `.meta.json`**: No bare artifacts. Contains validation scores and feedback.
3. **Critic is the only validator**: Producers do not self-validate. If a validation score is < 0.5, the critic logs failure patterns directly to `learnings.md`.
4. **Versioned, not overwritten**: All changes write to incremented versions (`v1`, `v2`, `v3`).
5. **`manifest.json` is the audit trail**: Required to be complete and finalized for a run to be considered "done".
6. **Research runs first**: Every input goes through `00_research` before `01_ingest`.
7. **Planning with Files**: Maintain a living checklist `task_plan.md` inside `outputs/<input_id>/` to coordinate steps.

---

## 💡 Quality Feedback Loop

```
[ Stage Agent Writes v1.json ]
            ↓
[ Critic runs validate_artifact() ]
            ↓
    Score < 0.5?
        ├── YES ──> [ Auto-log failure pattern to learnings.md ] ──> [ Send retry to Agent ]
        └── NO  ──> [ Record attempt as Pass ] ──> [ Advance Stage ]
```

When the Critic evaluates a stage and assigns an LLM-judge score below `0.5`, the validator automatically appends a detailed failure entry to `learnings.md` with the `@critic` tag. This allows subsequent agents to fetch matching historical failure contexts via the `memory_retriever` tool, avoiding repeating past errors.
