# Approval Gates

Use these gates before tool use:

| Action | Gate |
|---|---|
| Create a new file | Confirm target path and create-only mode. |
| Edit an existing file | Read current content and preserve unrelated user changes. |
| Delete or move files | Require explicit approval and rollback plan. |
| Read secrets | Require explicit task need and limited scope. |
| External read | Record source and date checked. |
| External write | Require destination, payload summary, and human approval. |
| Production data access | Require human approval and validation plan. |

Completion requires the relevant gate to be evaluated and reported.

