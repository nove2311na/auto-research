# Templates for 00-research

| File | Purpose |
|---|---|
| `v1.json.template` | Empty v1.json with all required fields + comments |
| `v1.meta.json.template` | (shared) Canonical meta block |

## Usage

The stage agent reads `v1.json.template` as a starting point, fills the fields, then `tools.artifact_io.write_artifact()`.
