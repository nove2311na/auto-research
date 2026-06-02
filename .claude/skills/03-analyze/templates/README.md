# Templates for 03-analyze

| File | Purpose |
|---|---|
| `v1.json.template` | Empty v1.json (themes, gaps, contradictions) |

Min constraints (target_state from skill spec refactor_delta):
- `themes[]`: 2-6 entries
- `gaps[]`: 1-5 entries
- `contradictions[]`: 0-3 entries
- Every theme.supporting_facts must reference a 02_extract fact verbatim
