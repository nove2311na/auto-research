"""tools — shared helpers used by all 8 agents in the research pipeline.

New in V2 (Claude Code-native rebuild):
  - spec_io: Draft-7 read/write/validate for the .claude/agents/*.json
    and .claude/skills/*/skill.json contracts (schemas/agent-spec.json,
    schemas/skill-spec.json).
"""
from . import spec_io  # noqa: F401 - re-export for package-level imports
