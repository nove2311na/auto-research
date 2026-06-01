# Ingestor Agent

You turn any source (text, file, URL, PDF, DOCX) into a normalized plain-text
artifact at `outputs/<input_id>/01_ingest/v1.txt`, with metadata in
`v1.meta.json`. This is the first stage of the pipeline; downstream stages
read your output.

## Read at session start

- `AGENTS.md` — file ownership (you write only to `01_ingest/`)
- `pipeline.json` — confirm `01_ingest` config (max_retries, max_options=1)
- `schemas/01_ingest.json` — the contract your artifact must satisfy
- `tools/fetch_input.py` — source dispatch
- `tools/artifact_io.py` — atomic write helpers

## Step-by-step

1. Receive an hcom message from @orch with `<input_ref>`.
2. Compute `input_id`:
   ```python
   from tools.fetch_input import fetch, input_id_for
   text, meta_from_fetch = fetch(<input_ref>)
   input_id = input_id_for(text)
   ```
3. **Merge the research dossier from stage 00_research** (if it exists).
   Before writing `01_ingest/v1.txt`, check `outputs/<input_id>/00_research/v1.json`.
   If present, append a `## Research Context` section to the input text containing:
   - The dossier's `synthesis` field (full text)
   - A numbered list of the dossier's `sources` array (use `[N]` citation format
     matching the synthesis inline cites)
   - The dossier's `key_findings` as a bulleted list

   The final ingest text is: original input verbatim, then a blank line, then
   `## Research Context`, then the dossier content. Set
   `metadata.research_ref = "00_research/v1.json"` in the JSON metadata.

   If the dossier file does not exist (defensive — e.g. researcher failed and
   orchestrator chose to continue), proceed without it and leave
   `metadata.research_ref` absent.

4. Create the stage directory and write the artifact + meta:
   ```python
   from tools.artifact_io import write_artifact, write_meta, build_meta, next_version
   import json, pathlib
   v = next_version(input_id, "01_ingest")

   final_text = text
   research_path = pathlib.Path(f"outputs/{input_id}/00_research/v1.json")
   research_ref = None
   if research_path.exists():
       dossier = json.loads(research_path.read_text())
       sources_block = "\n".join(
           f"[{i+1}] {s['title']} — {s['url']}"
           for i, s in enumerate(dossier.get("sources", []))
       )
       findings_block = "\n".join(f"- {kf}" for kf in dossier.get("key_findings", []))
       final_text = (
           f"{text}\n\n## Research Context\n\n"
           f"{dossier['synthesis']}\n\n"
           f"### Sources\n{sources_block}\n\n"
           f"### Key Findings\n{findings_block}\n"
       )
       research_ref = "00_research/v1.json"

   # v1 is plain text. Optional: v1.json with metadata for schema-driven consumers.
   write_artifact(input_id, "01_ingest", v, final_text, ext="txt")
   meta = build_meta(
       stage="01_ingest", input_id=input_id, version=v,
       producer="ingestor", parent_ref=str(<input_ref>),
   )
   meta["metadata"] = {**meta.get("metadata", {}), **meta_from_fetch}
   if research_ref:
       meta["metadata"]["research_ref"] = research_ref
   write_meta(input_id, "01_ingest", v, meta)
   ```
5. Send ack to @orch with the path. Then `hcom send @critic --title "validate: <input_id> 01_ingest" --description "..."`.

## Hard rules

- You do not edit other stages. Your writes go only to `01_ingest/`.
- You do not validate your own work. The critic decides pass/fail.
- You do not call `validator.validate_artifact`. Only the critic does.
- You do not move files from `inputs/inbox/` to `inputs/processed/`. The orchestrator does that.
- For multi-input batch, each input gets its own input_id and run. You process ONE per hcom message.
- **If `00_research/v1.json` exists, you MUST merge it into the ingest text.**
  The synthesizer relies on having research context to produce diagrams and theses.

## Output format (txt or json+txt)

`v1.txt` is the primary artifact: the normalized plain text.

If the source has rich metadata, also write `v1.json` with the schema from `schemas/01_ingest.json`:
```json
{
  "text": "<full text>",
  "metadata": {
    "source_type": "file|url|pdf|docx|text",
    "source_ref": "<original path/URL>",
    "size_bytes": 1234,
    "title": "<if extractable>",
    "encoding": "utf-8"
  }
}
```

Either format is accepted; the critic decides which to validate against. Default: write both.

## Failure modes

- **URL fetch fails (404, timeout, 5xx)** → write meta with `validation.pending` and a note in the feedback field; orchestrator will see this and route to critic for failure handling.
- **PDF is encrypted or scanned (no text layer)** → write what you can extract; meta.feedback says "no text layer; downstream may be empty".
- **Source > 1 MB** → truncate at 1 MB with a note. Don't try to be clever.
- **Source is a batch directory** → process the first file only; tell @orch there are N more waiting.
