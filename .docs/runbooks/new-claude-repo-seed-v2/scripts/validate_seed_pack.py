#!/usr/bin/env python3
"""Validate the New Claude Repo Seed V2 pack."""
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
    note: str = ""


CORE_REQUIREMENTS = [
    Requirement("README.md", note="pack entrypoint"),
    Requirement("seed_prompt.md", note="seed prompt"),
    Requirement("growth_protocol.md", note="idea germination protocol"),
    Requirement("v1_benchmark_contract.md", note="V1 benchmark contract"),
    Requirement("agent_skill_tool_matrix.md", note="agent skill tool matrix"),
    Requirement("mcp_catalog.md", note="MCP catalog and risk policy"),
    Requirement("reference_repo_index.md", note="source index"),
    Requirement("scaffold_output_contract.md", note="input and output contract"),
    Requirement("quality_rubric.md", note="seed rubric"),
    Requirement("comparison_note.md", note="V2 comparison deliverable"),
    Requirement("task_plan.md", note="planning with files"),
    Requirement("notes.md", note="implementation notes"),
    Requirement("schemas/seed_input.schema.json", note="seed input schema"),
    Requirement("schemas/agent_system_spec.schema.json", note="system spec schema"),
    Requirement("scripts/validate_seed_pack.py", note="pack validator"),
    Requirement("templates/CLAUDE.md", note="generated repo Claude entrypoint"),
    Requirement("templates/AGENTS.md", note="generated repo agent memory"),
    Requirement("templates/.mcp.json.example", note="generated repo MCP config sample"),
    Requirement("templates/.claude/settings.json.example", note="generated repo Claude settings sample"),
    Requirement("templates/.claude/agents/idea-harvester.md", note="seed intake subagent"),
    Requirement("templates/.claude/agents/reference-harvester.md", note="reference harvest subagent"),
    Requirement("templates/.claude/agents/system-architect.md", note="system architect subagent"),
    Requirement("templates/.claude/agents/scaffold-planner.md", note="scaffold planner subagent"),
    Requirement("templates/.claude/agents/gatekeeper.md", note="validation subagent"),
    Requirement("templates/.claude/skills/idea-germination/SKILL.md", note="idea germination skill"),
    Requirement("templates/.claude/skills/reference-harvest/SKILL.md", note="reference harvest skill"),
    Requirement("templates/agentic/knowledge/README.md", note="knowledge folder index"),
    Requirement("templates/agentic/README.md", note="agentic folder index"),
    Requirement("templates/agentic/memory/README.md", note="memory folder index"),
    Requirement("templates/agentic/policies/tool-risk-levels.md", note="tool risk policy"),
    Requirement("templates/agentic/policies/approval-gates.md", note="approval gate policy"),
    Requirement("templates/agentic/orchestration/README.md", note="orchestration folder index"),
    Requirement("templates/agentic/specs/agent-system-spec.md", note="system spec template"),
    Requirement("templates/agentic/evals/v1-benchmark-alignment.md", note="V1 benchmark eval"),
    Requirement("templates/scripts/gates/README.md", note="generated repo gates folder"),
    Requirement("templates/scripts/gates/validate_agentic_structure.py", note="V1-plus structure gate"),
    Requirement("templates/scripts/gates/run_quality_gate.py", note="quality gate"),
    Requirement("templates/scripts/gates/scan_secrets.py", note="secret scan gate"),
]

REQUIRED_PHRASES = {
    "scaffold_output_contract.md": ["seed_input", "agent_system_spec", "agents", "skills", "tools", "mcp_servers"],
    "v1_benchmark_contract.md": ["new-claude-repo", "V1", "V2", "v1_benchmark_alignment"],
    "agent_skill_tool_matrix.md": ["forbidden_actions", "allowed_tools", "stop_conditions", "escalation"],
    "mcp_catalog.md": ["risk_class", "approval", "auth"],
    "reference_repo_index.md": ["Distilled Takeaway", "npx -y skills add", "anthropics/skills"],
    "quality_rubric.md": ["Hard Gates", "Weighted Rubric", "agent_system_spec"],
    "templates/.claude/skills/idea-germination/SKILL.md": ["references/", "scripts/", "assets/"],
}

MARKER_PARTS = [
    ("T", "ODO"),
    ("T", "BD"),
    ("FIX", "ME"),
    ("lorem", " ipsum"),
    ("fake", "-url"),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def path_matches(path: Path, kind: str) -> bool:
    if kind == "dir":
        return path.is_dir()
    if kind == "file":
        return path.is_file()
    return path.exists()


def validate_json_file(path: Path) -> str | None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"invalid JSON: {exc}"
    except OSError as exc:
        return f"cannot read JSON: {exc}"
    return None


def find_markers(root: Path) -> list[str]:
    markers = ["".join(parts) for parts in MARKER_PARTS]
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            continue
        text = read_text(path)
        lowered = text.lower()
        for marker in markers:
            haystack = text if marker.isupper() else lowered
            needle = marker if marker.isupper() else marker.lower()
            if needle in haystack:
                findings.append(f"{path.relative_to(root)} contains marker {marker}")
    return findings


def validate(root: Path) -> dict[str, Any]:
    missing: list[str] = []
    empty: list[str] = []
    phrase_failures: list[str] = []
    json_failures: list[str] = []

    for requirement in CORE_REQUIREMENTS:
        path = root / requirement.path
        if not path_matches(path, requirement.kind):
            missing.append(requirement.path)
            continue
        if requirement.kind == "file" and not read_text(path).strip():
            empty.append(requirement.path)

    for relative_path, phrases in REQUIRED_PHRASES.items():
        text = read_text(root / relative_path)
        for phrase in phrases:
            if phrase not in text:
                phrase_failures.append(f"{relative_path} missing phrase {phrase}")

    for relative_path in (
        "schemas/seed_input.schema.json",
        "schemas/agent_system_spec.schema.json",
        "templates/.mcp.json.example",
        "templates/.claude/settings.json.example",
    ):
        failure = validate_json_file(root / relative_path)
        if failure:
            json_failures.append(f"{relative_path}: {failure}")

    marker_findings = find_markers(root)
    failures = missing + empty + phrase_failures + json_failures + marker_findings
    return {
        "target": str(root),
        "status": "pass" if not failures else "fail",
        "summary": {
            "requirements": len(CORE_REQUIREMENTS),
            "missing": len(missing),
            "empty": len(empty),
            "phrase_failures": len(phrase_failures),
            "json_failures": len(json_failures),
            "marker_findings": len(marker_findings),
        },
        "missing": missing,
        "empty": empty,
        "phrase_failures": phrase_failures,
        "json_failures": json_failures,
        "marker_findings": marker_findings,
    }


def print_human(report: dict[str, Any]) -> None:
    print("== Seed pack validation ==")
    print(f"target: {report['target']}")
    print(f"status: {report['status']}")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")

    for section in ("missing", "empty", "phrase_failures", "json_failures", "marker_findings"):
        items = report[section]
        if items:
            print(f"\n{section}:")
            for item in items:
                print(f"  - {item}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Seed pack folder to validate")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    report = validate(root)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human(report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
