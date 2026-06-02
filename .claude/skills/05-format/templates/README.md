# Templates for 05-format

| File | Purpose |
|---|---|
| `v1.json.template` | Empty v1.json with field-mapping hints |
| `v1.md.template` | Empty v1.md with section structure |

## Field mapping (verbatim from skill spec)

- `summary` <- `04_synthesize.summary` (verbatim, may lightly polish)
- `entities` <- `02_extract.entities` (deduped by name)
- `facts` <- `02_extract.facts` (top 10-20 by confidence)
- `analysis.themes` <- `03_analyze.themes[].name` + description
- `analysis.gaps` <- `03_analyze.gaps[].description`
- `analysis.contradictions` <- `03_analyze.contradictions[].explanation`
- `insights` <- `04_synthesize.insights[].insight`
- `diagrams` <- `04_synthesize.diagrams` (verbatim)
- `theses` <- `04_synthesize.theses` (verbatim)
- `references` <- `01_ingest.source_ref` + cited URLs

## Markdown wrapper

The formatter adds the ` ```mermaid ` wrapper when rendering v1.md. The 04_synthesize.diagrams[].code does NOT include the wrapper.
