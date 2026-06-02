"""activate_caveman.py — Cross-platform SessionStart hook for caveman mode.

Reads the caveman SKILL.md and emits a JSON string to stdout with additionalContext,
which Claude Code integrates automatically at session start.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    repo_root = Path(__file__).resolve().parents[2]
    skill_path = repo_root / ".claude" / "skills" / "caveman" / "SKILL.md"

    if not skill_path.exists():
        sys.exit(0)

    try:
        skill = skill_path.read_text(encoding="utf-8")
    except OSError:
        sys.exit(0)

    context = (
        "CAVEMAN MODE ACTIVE - level: full\n\n"
        "This project enables caveman automatically through a Claude Code SessionStart hook.\n"
        "Follow the project /caveman skill for every assistant response in this session "
        "unless the user says \"stop caveman\", \"normal mode\", or selects another caveman intensity.\n\n"
        f"Project skill path:\n{skill_path}\n\n{skill}"
    )

    output = {
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }

    sys.stdout.write(json.dumps(output, ensure_ascii=False))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
