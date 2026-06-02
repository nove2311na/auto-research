# Templates for 04-synthesize

| File | Purpose |
|---|---|
| `v1.json.template` | Empty v1.json with all required fields |
| `flowchart.mmd` (in fixtures/) | Mermaid flowchart example |
| `mindmap.mmd` (in fixtures/) | Mermaid mindmap example |

## Hard rules

- `diagrams[]` >= 2 entries, at least one flowchart AND one mindmap
- `theses[]` >= 2 entries
- `code` in each diagram is Mermaid syntax WITHOUT the ` ```mermaid ` wrapper (formatter adds it)
- No new facts in narrative/insights/theses — only from 02_extract.facts or 00_research.key_findings
