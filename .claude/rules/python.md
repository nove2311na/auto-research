---
paths:
  - "**/*.py"
  - "**/*.sh"
---

# Python style rules for the research-pipeline workspace

These apply whenever Claude Code is reading or editing `.py` or `.sh` files in this workspace.

## Hard invariants (overrides everything below)

1. **Never edit `pipeline.json` from an agent prompt.** It is the source of truth for stages + schemas. Humans edit it. If a stage is wrong, escalate.
2. **Never edit another agent's `outputs/<id>/<stage>/`.** Each agent owns its stage folder. Cross-stage data flows through hcom handoffs + the `parent_ref` in meta.
3. **Never self-validate.** The critic is the only validator. Stage agents do not call `tools.validator.validate_artifact()` on their own work.
4. **Never overwrite an artifact.** If you need to retry, write `v2` next to `v1`. Use `tools.artifact_io.next_version()` to find the next number.
5. **Every artifact needs a sibling `.meta.json`.** Use `tools.artifact_io.build_meta()` to construct, `write_meta()` to persist. The critic will overwrite the `validation` block — that's expected.

## Style

- Type hints on all function signatures.
- `pathlib.Path` over `os.path`.
- No `print()` for logging — use `logging` module. (Exception: CLI smoke blocks under `if __name__ == "__main__"` are fine.)
- `subprocess.run([...], check=True)` over `os.system`.
- Bash scripts: `set -euo pipefail` at the top.

## Imports

- Standard library first, third-party second, local third (with blank lines between).
- No wildcard imports.
- Local imports via `from tools.artifact_io import ...`, `from tools.validator import ...`, `from tools.fetch_input import ...`, `from tools.manifest import ...`.

## Comments

- One line, only when the WHY is non-obvious.
- No "what the code does" comments — the code says what.
- Reference `learnings.md` entries or `manifest.json` paths when relevant.

## Testing

- The 5-stage pipeline IS the integration test. For helper modules (`tools/*.py`), write at minimum an `if __name__ == "__main__"` smoke block. Real unit tests are V2.
- New tools added to `tools/` must come with a smoke test that runs in <5 seconds (no network, no LLM).
