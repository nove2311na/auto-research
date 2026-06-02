#!/usr/bin/env python3
"""Validate a Claude-native agentic repo scaffold.

This is a deterministic structure gate for generated or retrofitted agentic
repositories. It checks required files/folders by profile and emits both
missing-path diagnostics and a coarse score summary.

Reference location in this repo:
    .docs/runbooks/new-claude-repo/validate_agentic_structure.py

Recommended generated target location in a scaffolded repo:
    scripts/gates/validate_agentic_structure.py
"""
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
    kind: str = "any"
    weight: float = 1.0
    profile: str = "minimal"
    note: str = ""


PROFILE_ORDER = {"minimal": 0, "standard": 1, "full": 2}

REQUIREMENTS = [
    Requirement("CLAUDE.md", "file", 3, "minimal", "primary Claude Code briefing"),
    Requirement(".gitignore", "file", 1, "minimal", "local/private file protection"),
    Requirement(".claude/settings.json", "file", 3, "minimal", "permissions and hooks"),
    Requirement(".claude/rules/00-global.md", "file", 2, "minimal", "global behavior rule"),
    Requirement("scripts/gates", "dir", 2, "minimal", "deterministic gates folder"),
    Requirement("scripts/gates/run-quality-gate.sh", "file", 2, "minimal", "quality gate"),
    Requirement("scripts/gates/scan-secrets.sh", "file", 2, "minimal", "secret scan gate"),
    Requirement("agentic/README.md", "file", 1, "minimal", "agentic folder index"),
    Requirement("agentic/memory/memory-candidates.md", "file", 1, "minimal", "memory staging area"),
    Requirement(".claude/agents/planner.md", "file", 2, "standard", "planning subagent"),
    Requirement(".claude/agents/researcher.md", "file", 2, "standard", "discovery subagent"),
    Requirement(".claude/agents/implementer.md", "file", 2, "standard", "implementation subagent"),
    Requirement(".claude/agents/reviewer.md", "file", 2, "standard", "review subagent"),
    Requirement(".claude/agents/qa.md", "file", 2, "standard", "validation subagent"),
    Requirement(".claude/agents/security-reviewer.md", "file", 2, "standard", "security subagent"),
    Requirement(".claude/agents/lead-gatekeeper.md", "file", 2, "standard", "lead routing subagent"),
    Requirement(".claude/skills/plan-task/SKILL.md", "file", 2, "standard", "planning skill"),
    Requirement(".claude/skills/review-pr/SKILL.md", "file", 2, "standard", "review skill"),
    Requirement(".claude/skills/security-review/SKILL.md", "file", 2, "standard", "security skill"),
    Requirement(".claude/skills/quality-gate/SKILL.md", "file", 2, "standard", "quality skill"),
    Requirement("agentic/knowledge/project-overview.md", "file", 1, "standard", "project knowledge"),
    Requirement("agentic/knowledge/system-map.md", "file", 1, "standard", "system map"),
    Requirement("agentic/knowledge/auth-permissions.md", "file", 1, "standard", "auth map"),
    Requirement("agentic/policies/approval-gates.md", "file", 1, "standard", "approval policy"),
    Requirement("agentic/policies/tool-risk-levels.md", "file", 1, "standard", "tool risk policy"),
    Requirement("agentic/orchestration/modes.md", "file", 1, "standard", "orchestration modes"),
    Requirement("agentic/orchestration/handoff-contracts.md", "file", 1, "standard", "handoff contract"),
    Requirement(".claude/hooks", "dir", 2, "full", "hook folder"),
    Requirement(".claude/hooks/block-dangerous-bash.sh", "file", 2, "full", "dangerous command blocker"),
    Requirement(".claude/hooks/block-sensitive-read.sh", "file", 2, "full", "sensitive read blocker"),
    Requirement(".claude/hooks/block-risky-write.py", "file", 2, "full", "risky write blocker"),
    Requirement(".claude/hooks/log-tool-call.py", "file", 1, "full", "tool-call logging"),
    Requirement(".claude/skills/write-adr/SKILL.md", "file", 1, "full", "ADR skill"),
    Requirement(".claude/skills/memory-promote/SKILL.md", "file", 1, "full", "memory promotion skill"),
    Requirement("agentic/evals/rubric-default.md", "file", 1, "full", "default eval rubric"),
    Requirement("agentic/evals/golden-tasks", "dir", 1, "full", "golden tasks"),
    Requirement("agentic/evals/regression-cases", "dir", 1, "full", "regression cases"),
    Requirement("agentic/evals/red-team", "dir", 1, "full", "red-team cases"),
    Requirement("agentic/logs", "dir", 1, "full", "local generated logs"),
    Requirement(".mcp.json", "file", 1, "full", "project MCP config"),
    Requirement("scripts/gates/validate_agentic_structure.py", "file", 1, "full", "self structure gate"),
    Requirement("scripts/gates/validate-migration.py", "file", 1, "full", "migration gate"),
    Requirement("scripts/gates/validate-memory-card.py", "file", 1, "full", "memory validation gate"),
]

HARD_GATES = [
    "CLAUDE.md",
    ".claude/settings.json",
    "scripts/gates",
]


def requirement_applies(requirement: Requirement, profile: str) -> bool:
    return PROFILE_ORDER[requirement.profile] <= PROFILE_ORDER[profile]


def path_ok(root: Path, requirement: Requirement) -> bool:
    path = root / requirement.path
    if requirement.kind == "file":
        return path.is_file()
    if requirement.kind == "dir":
        return path.is_dir()
    return path.exists()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def settings_checks(root: Path) -> list[dict[str, Any]]:
    settings_path = root / ".claude" / "settings.json"
    checks: list[dict[str, Any]] = []
    if not settings_path.exists():
        return checks
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [{"status": "fail", "check": "settings_json_parse", "message": str(exc)}]

    serialized = json.dumps(data).lower()
    checks.append({
        "status": "pass" if ".env" in serialized else "warn",
        "check": "settings_blocks_env",
        "message": "settings references .env protection" if ".env" in serialized else "settings does not visibly mention .env",
    })
    checks.append({
        "status": "pass" if "rm -rf" in serialized or "dangerous" in serialized else "warn",
        "check": "settings_blocks_destructive",
        "message": "settings references destructive command protection"
        if "rm -rf" in serialized or "dangerous" in serialized
        else "settings does not visibly mention destructive command protection",
    })
    return checks


def claude_md_checks(root: Path) -> list[dict[str, Any]]:
    path = root / "CLAUDE.md"
    if not path.exists():
        return []
    text = read_text(path)
    lines = text.splitlines()
    checks = [
        {
            "status": "pass" if len(lines) <= 220 else "warn",
            "check": "claude_md_length",
            "message": f"CLAUDE.md has {len(lines)} lines",
        },
        {
            "status": "pass" if "commands" in text.lower() or "common command" in text.lower() else "warn",
            "check": "claude_md_commands",
            "message": "CLAUDE.md documents commands" if "commands" in text.lower() else "CLAUDE.md may not document commands",
        },
        {
            "status": "pass" if "secret" in text.lower() or ".env" in text.lower() else "warn",
            "check": "claude_md_safety",
            "message": "CLAUDE.md mentions secret/env safety" if "secret" in text.lower() or ".env" in text.lower() else "CLAUDE.md may not mention secret/env safety",
        },
    ]
    return checks


def score_to_readiness(score: float, hard_failed: list[str]) -> str:
    if hard_failed:
        return "block"
    if score >= 4.3:
        return "excellent"
    if score >= 3.8:
        return "production_ready_baseline"
    if score >= 3.2:
        return "usable_needs_hardening"
    return "needs_revision"


def validate(root: Path, profile: str) -> dict[str, Any]:
    applicable = [req for req in REQUIREMENTS if requirement_applies(req, profile)]
    rows = []
    total_weight = sum(req.weight for req in applicable) or 1.0
    earned = 0.0
    missing = []
    for req in applicable:
        ok = path_ok(root, req)
        if ok:
            earned += req.weight
        else:
            missing.append(req.path)
        rows.append({
            "path": req.path,
            "kind": req.kind,
            "profile": req.profile,
            "weight": req.weight,
            "status": "pass" if ok else "fail",
            "note": req.note,
        })

    hard_failed = [path for path in HARD_GATES if not (root / path).exists()]
    raw_ratio = earned / total_weight
    score = round(1.0 + raw_ratio * 4.0, 2)
    soft_checks = [*claude_md_checks(root), *settings_checks(root)]
    warn_count = sum(1 for check in soft_checks if check["status"] == "warn")
    fail_count = len(missing)

    return {
        "target": str(root),
        "profile": profile,
        "score": score,
        "readiness": score_to_readiness(score, hard_failed),
        "summary": {
            "requirements": len(applicable),
            "passed": len(applicable) - fail_count,
            "failed": fail_count,
            "warnings": warn_count,
            "hard_gates_failed": hard_failed,
        },
        "missing": missing,
        "requirements": rows,
        "soft_checks": soft_checks,
    }


def print_human(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("== Agentic structure validation ==")
    print(f"target:    {report['target']}")
    print(f"profile:   {report['profile']}")
    print(f"score:     {report['score']}/5")
    print(f"readiness: {report['readiness']}")
    print(f"passed:    {summary['passed']}/{summary['requirements']}")
    print(f"warnings:  {summary['warnings']}")
    if summary["hard_gates_failed"]:
        print("\nHard gates failed:")
        for item in summary["hard_gates_failed"]:
            print(f"  - {item}")
    if report["missing"]:
        print("\nMissing required paths:")
        for item in report["missing"]:
            print(f"  - {item}")
    warnings = [check for check in report["soft_checks"] if check["status"] == "warn"]
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning['check']}: {warning['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Repository root to validate")
    parser.add_argument("--profile", choices=sorted(PROFILE_ORDER), default="standard")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as missing requirements")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    report = validate(root, args.profile)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human(report)

    has_failures = bool(report["missing"] or report["summary"]["hard_gates_failed"])
    has_warnings = bool(report["summary"]["warnings"])
    if has_failures or (args.strict and has_warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
