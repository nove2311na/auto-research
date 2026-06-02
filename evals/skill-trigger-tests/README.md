# Skill trigger tests

For each skill, assert the right one fires for the right input.

| Input shape | Expected skill |
|---|---|
| `topic="..."` (no input_ref) | 00-research |
| `input_ref=path/to/file` | 01-ingest |
| `input_ref=url` | 01-ingest |
| `01_ingest/v1.txt` exists | 02-extract |
| `02_extract/v1.json` (winner) | 03-analyze |
| `03_analyze/v1.json` | 04-synthesize |
| `04_synthesize/v1.json` | 05-format |
| any artifact | 06-validate (critic) |

Each row = `{input_shape, expected_skill, test_call}` in `tests.json`.
