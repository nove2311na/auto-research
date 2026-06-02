# Handoff Contracts

## PM to Operator: Figma Extraction

Required input:

- Figma URL or node IDs,
- project name,
- output section ID,
- required workspace paths.

Required output:

- `workspace/rawdata/[section_id]_raw.json`,
- `workspace/contents/[section_id]_content.json`,
- extraction summary.

## PM to Architect: Blueprint

Required input:

- raw data path,
- content path,
- design-system path,
- target page context.

Required output:

- blueprint JSON path,
- page structure update,
- approval summary.

## PM to Operator: Webflow Build

Required input:

- approved blueprint path,
- Webflow site ID,
- Webflow page ID,
- MCP-352 constraints.

Required output:

- action log,
- verification points,
- blockers.

## PM to Architect: QA

Required input:

- approved blueprint,
- Webflow state/snapshot,
- build action log.

Required output:

- `[APPROVED]` or `[FIX]`,
- evidence,
- error log entries.

