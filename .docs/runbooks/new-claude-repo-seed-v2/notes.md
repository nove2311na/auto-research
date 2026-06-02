# Notes

## Decisions

- The V2 folder is separate from `.docs/runbooks/new-claude-repo/`.
- The seed is docs, templates, schemas, and a validator, not a full generator CLI.
- External repositories are not vendored. The reference index stores links, observed CLI results, and distilled takeaways.
- Default write policy for generated scaffold files is `create_only`.
- MCP server access is designed through risk class, auth, approval policy, and allowed agents before configuration.
- `.docs/runbooks/new-claude-repo/` is now the mandatory benchmark. V2-generated repos must match or exceed V1 architecture, structure validation, and rubric targets before claiming readiness.

## Local Evidence

- `.docs/runbooks/new-claude-repo-seed-v2/` did not exist before creation.
- The existing V1 pack contains README, blueprint, rubric, movable layout tips, validator, and source material.
- The local `python-code-style` skill was used for the validator style: type hints, descriptive names, standard library only, and clear docstrings.
- `rtk` command wrapping failed in this sandbox with `windows sandbox: spawn setup refresh`, so direct narrow PowerShell and `rg` commands were used.
- The first validator run exposed strict UTF-8 reading on non-text files. The validator now ignores undecodable bytes during text scans.

## Reference-Learning Results

- `anthropics/skills`: 18 skills found.
- `shakacode/claude-code-commands-skills-agents`: 1 docs skill found.
- `awrshift/claude-memory-kit`: 3 skills found.
- `enc0ding/claude-agent-starter`: 1 installer classification skill found.
- `OneWave-AI/claude-skills`: 154 skills found.
