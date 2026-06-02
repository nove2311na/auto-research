# Eval cases — 03-analyze

## Case A1: well-extracted input
- **Input:** 02_extract/v1.json (the QEC winner, ~10 facts, 5 entities, 2 quotes)
- **Expected:** themes[2-6], gaps[1-5], contradictions[0-3]
- **Pass:** every theme's supporting_facts references an existing fact; LLM-judge >= 0.7

## Case A2: empty 02_extract
- **Input:** 02_extract/v1.json = {entities:[], facts:[], quotes:[]}
- **Expected:** {themes:[], gaps:["whole-topic-is-empty"], contradictions:[]}
- **Pass:** schema check passes; critic fails (no themes); orchestrator halts

## Case A3: too-short source
- **Input:** 02_extract with 1 fact, 1 entity
- **Expected:** 1 theme is OK (do not pad to 6)
- **Pass:** themes[1]; gap notes the brevity
