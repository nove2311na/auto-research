# Skill 01 — Ingest

## Identity

| Field | Value |
|---|---|
| Stage id | `01_ingest` |
| Owning agent | `ingestor` |
| Schema | `schemas/01_ingest.json` (for the JSON variant; TXT variant is `ext="txt"`) |
| Output format | `txt` (primary) + `json` (optional) |
| `max_options` | 1 |
| `max_retries` | 3 |
| Antonio Gulli patterns | Ch. 5 Tool Use, Ch. 10 MCP (file-type dispatch) |
| Claude Code book chapters | Ch. 5 MCP |

## Input schema

### Fields

| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes (computed by agent from text) | derived via `tools.fetch_input.input_id_for(text)` |
| `input_ref` | string (path/URL/topic) | yes | hcom message from `@orch` |
| (optional) `00_research/v1.json` | file path | no (defensive: missing → proceed without merge) | sibling file in `outputs/<id>/` |

### Example hcom message

```bash
hcom send --name <sender> "@research-pipeline-claude-2 ingest: abc12345; input=inputs/inbox/qec.txt; write outputs/abc12345/01_ingest/v1.txt + v1.meta.json"
```

### Source

- `schemas/01_ingest.json` — required: `text` (minLength 1), `metadata` (`source_type`, `source_ref`, `size_bytes`)
- `agents/ingestor/AGENT.md:18-25` — input prose

## Process

1. **(deterministic)** Read hcom message. Extract `input_ref`.
2. **(deterministic)** Call `tools.fetch_input.fetch(<input_ref>)` → `(text, meta_from_fetch)`. Compute `input_id = tools.fetch_input.input_id_for(text)`.
3. **(LLM-decided / deterministic hybrid)** **Merge the research dossier from `00_research/v1.json`** (if it exists):
   - If `outputs/<id>/00_research/v1.json` exists:
     - Read the dossier.
     - Build the `## Research Context` block (see Output schema below).
     - Append to `text` → `final_text = f"{text}\n\n## Research Context\n\n<dossier>..."`.
     - Set `meta["metadata"]["research_ref"] = "00_research/v1.json"`.
   - If missing (defensive): proceed without it; leave `metadata.research_ref` absent.
4. **(deterministic)** Write `v1.txt` (the primary artifact) via `tools.artifact_io.write_artifact`:
   ```python
   v = next_version(input_id, "01_ingest")
   write_artifact(input_id, "01_ingest", v, final_text, ext="txt")
   ```
5. **(LLM-decided, optional)** If the source has rich metadata, also write `v1.json` matching `schemas/01_ingest.json` with `text` + `metadata`.
6. **(deterministic)** Build + write meta:
   ```python
   meta = build_meta(stage="01_ingest", input_id=input_id, version=v,
                     producer="ingestor", parent_ref=str(input_ref))
   meta["metadata"] = {**meta.get("metadata", {}), **meta_from_fetch}
   if research_ref:
       meta["metadata"]["research_ref"] = research_ref
   write_meta(input_id, "01_ingest", v, meta)
   ```
7. **(deterministic)** Ack to `@orch` with the path. Then ping `@critic` with `validate: <input_id> 01_ingest`.

### Merge format (when dossier is present)

```
<original input verbatim>

## Research Context

<dossier.synthesis>

### Sources
[1] <title> — <url>
[2] <title> — <url>
...

### Key Findings
- <finding 1>
- <finding 2>
...
```

(Lifted from `agents/ingestor/AGENT.md:57-62` and `scripts/smoke_v2.py:48-62`.)

## Output schema (artifact template)

### Primary: `v1.txt` (plain text)

Plain text. The `## Research Context` block is appended only if the dossier exists.

### Optional: `v1.json` (matches `schemas/01_ingest.json`)

```json
{
  "text": "<full text including the Research Context block if merged>",
  "metadata": {
    "source_type": "text|file|url|pdf|docx|batch_dir",
    "source_ref": "<original path/URL>",
    "size_bytes": 1234,
    "fetched_at": "2026-06-01T12:00:00Z",
    "encoding": "utf-8",
    "title": "<if extractable>",
    "research_ref": "00_research/v1.json"
  }
}
```

### Meta: `v1.meta.json`

Built via `tools.artifact_io.build_meta` (default validation: pending). Enriched with `metadata` from `fetch_input` and (optionally) `metadata.research_ref`.

## Example

### Real (lifted from `scripts/smoke_v2.py:48-71`)

The `v1.json` variant after a successful run:

```json
{
  "text": "Quantum error correction 2026\n\n## Research Context\n\nQuantum error correction matured significantly in 2026...\n\n**Sources:**\n[1] QEC Review 2026 — https://example.com/qec-review-2026\n[2] Google Condor Update — https://example.com/google-condor-2025\n\n**Key findings:**\n- Surface codes crossed the 1000 logical qubit milestone in 2026\n- Below-threshold operation now routine for distances d=5 to d=11\n- Real-time decoding latency remains the bottleneck for fault-tolerant gates\n",
  "metadata": {
    "source_type": "text",
    "source_ref": "inputs/inbox/qec.txt",
    "size_bytes": 580,
    "research_ref": "00_research/v1.json"
  }
}
```

The `v1.txt` is the same content as `text` above. The `v1.meta.json` has `producer: "ingestor"`, `validation: pending`, `parent_ref: "inputs/inbox/qec.txt"`, and the metadata block from `v1.json` merged in.

## Self-check checklist (pre-submit, numbered)

- [ ] **TXT non-empty:** `v1.txt` is non-empty UTF-8
- [ ] **Dossier merged if exists:** if `00_research/v1.json` was present, `v1.txt` ends with `## Research Context` block
- [ ] **Citations in merged block:** contains `[1]`, `[2]`, etc., matching the dossier's `sources[]` indices
- [ ] **research_ref set:** if dossier was merged, `v1.meta.json#metadata.research_ref = "00_research/v1.json"`
- [ ] **Defensive case:** if dossier was absent, `research_ref` is absent (not `null`, not `""`)
- [ ] **Meta complete:** `v1.meta.json` has `producer: "ingestor"`, `validation.status: "pending"`, `parent_ref: <input_ref>`
- [ ] **Handoff:** `@critic` pinged with `validate: <input_id> 01_ingest`

## Validation

- **Which check:** `validation/02-post-execution-completeness.md` (JSON variant) + `validation/03-llm-judge.md`. For TXT variant, schema+completeness return `skip` per `tools/validator.py:118-126`; only the LLM-judge applies.
- **Threshold:** 0.7
- **Common failure → fix:**
  - TXT empty → agent failed to fetch / wrote nothing → re-fetch with longer timeout
  - JSON `text` empty or `metadata.source_type` invalid → check fetch_input dispatch
  - LLM-judge low (e.g. "dossier not merged") → re-run, ensure `00_research/v1.json` is read first

## Failure modes

- **URL fetch fails (404, timeout, 5xx)** → write meta with `validation.pending` and a note in the feedback field; orchestrator routes to critic for failure handling. (`agents/ingestor/AGENT.md:110`)
- **PDF is encrypted or scanned (no text layer)** → write what you can extract; meta.feedback says "no text layer; downstream may be empty". (`:111`)
- **Source > 1 MB** → truncate at 1 MB with a note. Don't try to be clever. (`:112`)
- **Source is a batch directory** → process the first file only; tell @orch there are N more waiting. (`:113`)
- **Defensive: `00_research/v1.json` missing** → proceed without merging; leave `metadata.research_ref` absent. (`:38-39`)

## Refactor delta

- **Scope:** Small
- **Current state:** 5-step process + 30 lines of merge code inlined in `agents/ingestor/AGENT.md:42-75`. No numbered pre-submit checklist.
- **Target state:** This skill spec owns the merge logic + the checklist. The agent's AGENT.md trims to ~50 lines.
- **Concrete steps:**
  1. Move the merge code block (`agents/ingestor/AGENT.md:47-63`) into this spec's Process step 3. Done (above).
  2. Add a "JSON variant" to the schema's `metadata` block: ensure `research_ref` is explicitly optional in `schemas/01_ingest.json` (currently is).
  3. Add `metadata.fetched_at` as `required` (currently optional) — every ingest should record when it was fetched.
  4. Cite this spec from `agents/ingestor/AGENT.md` "Step-by-step" section.

## Source files (for traceability)

- `agents/ingestor/AGENT.md` — runtime prompt
- `schemas/01_ingest.json` — the contract
- `tools/fetch_input.py` — `fetch`, `input_id_for`, `move_to_processed`
- `tools/artifact_io.py` — `write_artifact`, `write_meta`, `build_meta`
- `AGENTS.md` invariant #6 — research first
- `agents/orchestrator/AGENT.md:51-55` — inbound handoff template
- `scripts/smoke_v2.py:48-71` — real example
