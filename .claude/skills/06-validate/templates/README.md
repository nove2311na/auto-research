# Templates for 06-validate

| File | Purpose |
|---|---|
| `validation-block.template` | The validation block the critic writes to `v<N>.meta.json` |

The critic does NOT produce content artifacts. It writes the `validation` block of the existing meta.json (and, for multi-option, calls `pick_winner` to copy the chosen option to stage root).
