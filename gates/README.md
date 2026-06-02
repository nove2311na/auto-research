# Gates — rule-based checkpoints

Rule-based gates run before / after an action. If a script can validate it, do not rely on prompt.

## Structure

```
gates/
├── input-gates/          # before stage starts: is the input complete?
├── plan-gates/           # between planning + implementation
├── implementation-gates/ # after a stage writes an artifact
├── output-gates/         # the JSON schema check (already in PreToolUse hook)
├── security-gates/       # secrets, dangerous paths, auth changes
├── test-gates/           # tests pass before promoting
├── release-gates/        # before marking input_id done
└── memory-promotion-gates/  # before writing to long-term memory
```

Python implementations now live in `src/research_pipeline/gates/*.py`. Root `gates/*.py`
files are compatibility shims so older imports such as `from gates.output_gates import ...`
continue to work.

## Convention

Every gate = 1 Python file with one `gate(input)` function that returns:

```python
{"status": "pass|fail", "summary": "...", "evidence": [...], "risks": [...]}
```

If `status="fail"`, the orchestrator halts (or revises plan, per gate type).

## Implemented gates

- `output-gates/json_schema_gate.py` — schema check on every artifact (called by `.claude/hooks/PreToolUse.py` + `tools/validator.py`)
- `input-gates/completeness_gate.py` — input_id has goal + scope + acceptance criteria
- `security-gates/path_safety_gate.py` — never write to blocked paths
- `output-gates/llm_judge_gate.py` — score threshold check
- `output-gates/manifest_consistency_gate.py` — winner matches options, no orphan meta files

## Implemented as Claude Code hooks

- `PreToolUse.py` runs `output-gates/json_schema_gate.py` for `outputs/<id>/<stage>/v<N>.<ext>` writes.

## Output schema (canonical)

```json
{
  "status": "pass|fail",
  "summary": "string",
  "evidence": ["string"],
  "risks": [
    {"severity": "low|medium|high|critical",
     "description": "string",
     "required_fix": "string"}
  ]
}
```
