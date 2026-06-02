#!/usr/bin/env python3
"""Validate a V1-plus Claude Code agentic repo scaffold."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Requirement:
    path: str
    kind: str = "file"
    profile: str = "standard"
    note: str = ""


PROFILE_ORDER = {"minimal": 0, "standard": 1, "full": 2}

REQUIREMENTS = [
    Requirement("CLAUDE.md", profile="minimal", note="Claude Code entrypoint"),
    Requirement("AGENTS.md", profile="minimal", note="agent team memory"),
    Requirement(".claude/agents", "dir", "minimal", "bounded agent roles"),
    Requirement(".claude/skills", "dir", "minimal", "reusable skills"),
    Requirement("agentic/README.md", profile="minimal", note="agentic folder index"),
    Requirement("agentic/knowledge", "dir", "minimal", "durable knowledge"),
    Requirement("agentic/memory", "dir", "minimal", "memory layer"),
    Requirement("agentic/policies", "dir", "minimal", "risk policies"),
    Requirement("scripts/gates", "dir", "minimal", "validation gates"),
    Requirement("scripts/gates/run_quality_gate.py", profile="minimal", note="quality gate"),
    Requirement("scripts/gates/scan_secrets.py", profile="minimal", note="secret scan"),
    Requirement("agentic/orchestration", "dir", "standard", "workflow contracts"),
    Requirement("agentic/specs/agent-system-spec.md", profile="standard", note="V2 system spec"),
    Requirement("agentic/evals/v1-benchmark-alignment.md", profile="standard", note="V1 benchmark eval"),
    Requirement(".claude/settings.json", profile="full", note="Claude settings"),
    Requirement(".mcp.json", profile="full", note="project MCP config"),
]


def applies(requirement: Requirement, profile: str) -> bool:
    return PROFILE_ORDER[requirement.profile] <= PROFILE_ORDER[profile]


def exists(root: Path, requirement: Requirement) -> bool:
    path = root / requirement.path
    if requirement.kind == "dir":
        return path.is_dir()
    return path.is_file()


def validate(root: Path, profile: str) -> dict[str, Any]:
    applicable = [requirement for requirement in REQUIREMENTS if applies(requirement, profile)]
    missing = [requirement.path for requirement in applicable if not exists(root, requirement)]
    return {
        "target": str(root),
        "profile": profile,
        "status": "pass" if not missing else "fail",
        "summary": {
            "requirements": len(applicable),
            "passed": len(applicable) - len(missing),
            "missing": len(missing),
        },
        "missing": missing,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Repo root to validate")
    parser.add_argument("--profile", choices=sorted(PROFILE_ORDER), default="standard")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    report = validate(Path(args.target).resolve(), args.profile)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("== V1-plus agentic structure validation ==")
        print(f"target: {report['target']}")
        print(f"profile: {report['profile']}")
        print(f"status: {report['status']}")
        print(f"passed: {report['summary']['passed']}/{report['summary']['requirements']}")
        if report["missing"]:
            print("\nMissing:")
            for item in report["missing"]:
                print(f"  - {item}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

