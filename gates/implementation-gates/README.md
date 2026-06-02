# Implementation gates

## `code_quality_gate.py` (V2 follow-up)
- **When:** after a stage's deterministic writes are done, before meta.validation=pass.
- **Checks:** pnpm lint, pnpm typecheck, pnpm test, pnpm build (per project type).
- **On fail:** retry once; on 2nd fail, halt.

Not yet implemented in V1 (the research-pipeline is data-in/data-out, no code in stages).
