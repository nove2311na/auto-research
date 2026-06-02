---
name: memory-retrieval
description: >
  Retrieve past lessons and failure patterns from the append-only learnings.md
  and archived learnings files. Use this skill at session start or during halts
  to cross-reference errors with previously documented lessons.
---

# Skill: Memory Retrieval

## Identity
- Owning tool/module: `research_pipeline.tools.memory_retriever`
- Output format: Console text output / python string list
- Triggers: Triggered when agent needs to lookup past lessons, resolutions of previous failures, or check context of a specific error keyword.

## Input Schema
| Field | Type | Required | Source | Description |
|---|---|---|---|---|
| `keyword` | string | yes | agent query | Keyword/topic to search in learnings (e.g. "timeout", "JSON parse", "citation") |

## Process

1. Identify search keyword from current runtime failure or context.
2. Invoke the tool:
   ```bash
   python -m research_pipeline.tools.memory_retriever "<keyword>"
   ```
3. Read the output. The tool searches:
   - `learnings.md` (active learnings)
   - `learnings.archive/*.md` (archived historical learnings)
4. Extract matching lessons, review context, changes tried, and lessons learned.
5. Apply findings to the current pipeline state/execution to resolve or avoid issues.

## Output Example
```markdown
=== Found 1 past lessons matching 'timeout' ===
## 2026-06-01 10:30 | @researcher | Timeout on fetching academic PDFs
- context: Attempting to download large PDFs during the research stage
- change: Added a timeout parameter of 30 seconds and fallback mechanism
- metric: retry success rate improved from 20% to 95%
- lesson: Always specify timeouts for requests and fall back gracefully
```

## Self-check
- Search keywords are specific (avoid overly generic terms like "error" unless checking all history).
- Verify both active and archived learnings are checked.
- Incorporate lessons into plans/decisions when encountering similar failures.
