#!/usr/bin/env python3
"""Run a lightweight quality gate for a V1-plus agentic repo."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_TEXT = {
    "CLAUDE.md": ["secret", "commands"],
    "AGENTS.md": ["Hard Invariants", "Current Agent Team"],
    "agentic/specs/agent-system-spec.md": ["V1 Benchmark Alignment", "Agents", "Workflows"],
    "agentic/policies/tool-risk-levels.md": ["R0", "R4"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, phrases in REQUIRED_TEXT.items():
        text = read_text(root / relative_path)
        if not text.strip():
            failures.append(f"{relative_path} is missing or empty")
            continue
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{relative_path} missing phrase {phrase}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Repo root to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.target).resolve())
    if failures:
        print("quality gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("quality gate: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

