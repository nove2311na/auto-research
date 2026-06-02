# Pipeline Start Guide

Use these commands from the repo root:

```cmd
cd /d G:\My Drive\10_Learning\_Research\auto-research
```

## 1. Check auth and quota

Make sure Claude/API auth is valid and quota is available. If Claude agents are out of quota, the Python scripts can still initialize and send hcom messages, but the 6-stage pipeline will not progress.

## 2. Launch the swarm

```cmd
python scripts\launch.py
```

This launches 8 hcom/Claude agents with deterministic routing tags:

- `@research-pipeline-claude-1` orchestrator
- `@research-pipeline-claude-8` researcher
- `@research-pipeline-claude-2` ingestor
- `@research-pipeline-claude-3` extractor
- `@research-pipeline-claude-4` analyzer
- `@research-pipeline-claude-5` synthesizer
- `@research-pipeline-claude-6` critic
- `@research-pipeline-claude-7` formatter

## 3. Check status

```cmd
python scripts\status.py
```

Look for active/listening agents. Stale agents will not read new hcom messages.

## 4. Send a research topic

```cmd
python scripts\run_pipeline.py --depth medium "Quantum error correction 2026"
```

Depth options:

```cmd
python scripts\run_pipeline.py --depth shallow "short topic"
python scripts\run_pipeline.py --depth medium "normal topic"
python scripts\run_pipeline.py --depth deep "research-heavy topic"
```

## 5. Track progress

```cmd
python scripts\status.py
```

The run is complete when the input shows `6/6 stages done`.

## 6. Read the final report

```cmd
type outputs\<input_id>\05_format\v1.md
```

For example:

```cmd
type outputs\3e9ddb4a\05_format\v1.md
```

## Notes

- `python scripts\kickoff.py` is only for sending a kickoff/reminder message to the orchestrator.
- `python scripts\run_pipeline.py ...` is the command that gives the system a real research topic.
- The scripts automatically set `HCOM_DIR` to the repo-local `.hcom` folder and reclaim the `bigboss` sender identity.

