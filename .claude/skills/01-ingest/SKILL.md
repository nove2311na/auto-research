---
name: 01-ingest
description: >
  Normalizes any source (text/URL/PDF/DOCX) to plain text at 01_ingest/v1.txt;
  merges the 00_research dossier if present. Use when the researcher stage
  finished and the orchestrator hands off to the ingestor.
---

# Skill 01 — Ingest

## Identity
- Stage id: `01_ingest`
- Owning agent: `ingestor`
- Schema: `schemas/01_ingest.json` (required: `text`, `metadata` with `source_type`/`source_ref`/`size_bytes`)
- Output format: `txt` (primary) + `json` (optional)
- `max_options`: 1, `max_retries`: 3

## Input schema
| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes (computed) | derived via `tools.fetch_input.input_id_for(text)` |
| `input_ref` | string (path/URL/topic) | yes | hcom message from `@orch` |
| (optional) `00_research/v1.json` | file path | no (defensive: missing → proceed) | sibling file in `outputs/<id>/` |

## Process (see `skill.json#process` for the structured form)

1. **(deterministic)** Read hcom message. Extract `input_ref`.
2. **(deterministic)** Call `tools.fetch_input.fetch(<input_ref>)` → `(text, meta_from_fetch)`. Compute `input_id`.
3. **(LLM + deterministic)** **Merge the research dossier from `00_research/v1.json`** (if exists):
   - Build `## Research Context` block: dossier `synthesis` + numbered `[N]` sources + `key_findings` bullets.
   - `final_text = f"{text}\n\n## Research Context\n\n..."`
   - Set `meta["metadata"]["research_ref"] = "00_research/v1.json"`.
   - If missing (defensive): proceed without it.
4. **(deterministic)** Write `v1.txt` via `write_artifact(..., ext="txt")`.
5. **(LLM-decided, optional)** If source has rich metadata, also write `v1.json`.
6. **(deterministic)** Build + write meta via `build_meta` + `write_meta`.
7. **(deterministic)** Ack to `@orch` with the path. Ping `@critic`.

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

## Output schema (artifact template)
See `skill.json#output_schema` for the JSON form.

Primary: `v1.txt` (plain text, with the `## Research Context` block if dossier exists).

Optional: `v1.json` matching `schemas/01_ingest.json`:
```json
{
  "text": "<full text including Research Context>",
  "metadata": {
    "source_type": "text|file|url|pdf|docx|batch_dir",
    "source_ref": "<original path/URL>",
    "size_bytes": 1234,
    "research_ref": "00_research/v1.json"
  }
}
```

## Self-check (see `skill.json#self_check` for the full numbered list)
- `v1.txt` is non-empty UTF-8
- If `00_research/v1.json` was present, `v1.txt` ends with `## Research Context` block
- Citations in merged block contain `[1]`, `[2]`, etc., matching dossier `sources[]` indices
- If dossier was merged, `v1.meta.json#metadata.research_ref = "00_research/v1.json"`
- If dossier was absent, `research_ref` is absent (not `null`, not `""`)
- `v1.meta.json` has `producer: "ingestor"`, `validation.status: "pending"`

## Validation
- For TXT variant: schema+completeness return `skip` (per `tools/validator.py:118-126`); only LLM-judge applies
- For JSON variant: full deterministic check
- Common failure: TXT empty → agent failed to fetch; re-fetch with longer timeout

## Source
Full spec: `.docs/agentic/skills/01-ingest.md`. JSON form: `.claude/skills/01-ingest/skill.json`. Real example: `scripts/smoke_v2.py:48-71`.
