# Eval cases — 01-ingest

## Case I1: local text file
- **Input:** input_ref=path/to/file.txt
- **Expected:** v1.txt = file content UTF-8; v1.json = {text, metadata: {source_ref, fetched_at}}
- **Pass:** text non-empty; metadata.fetched_at present

## Case I2: URL fetch 404
- **Input:** input_ref=https://example.com/does-not-exist
- **Expected:** v1.txt empty or "fetch failed"; meta.feedback = "404"
- **Pass:** meta written with validation.pending + feedback mentions the 404
- **Failure mode:** silent empty ingest with no meta feedback

## Case I3: 00_research/v1.json exists (merge case)
- **Input:** input_ref=url + 00_research/v1.json present
- **Expected:** v1.txt ends with `## Research Context` block + numbered [N] sources + key_findings bullets
- **Pass:** v1.txt contains "## Research Context"; meta.metadata.research_ref = "00_research/v1.json"

## Case I4: input > 1 MB
- **Input:** input_ref=large-file.txt (1.5 MB)
- **Expected:** v1.txt truncated at 1 MB; meta.feedback notes truncation
- **Pass:** v1.txt length <= 1 MB; meta.feedback mentions truncation
