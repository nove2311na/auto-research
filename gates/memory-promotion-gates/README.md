# Memory promotion gates

## `learning_promotion_gate.py` (V2 follow-up)
- **When:** before a session's learnings are written to long-term `learnings.md`.
- **Checks:** the learning is non-trivial (not "I forgot to import X"), 2+ corroborating sessions, human-reviewed.
- **On fail:** write to `learnings.draft.md` instead.

Not yet implemented in V1.
