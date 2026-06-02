#!/usr/bin/env python3
"""validate_specs.py — validate all .claude/ agents and skills against the JSON Schema contracts.

Drives tools.spec_io for I/O + cross-link, then prints a per-spec pass/fail
summary. Exit code 0 if every spec is valid AND cross-link is clean; 1 otherwise.

Usage:
    python scripts/validate_specs.py                # validate all
    python scripts/validate_specs.py --strict       # also fail on warnings
    python scripts/validate_specs.py --agent NAME   # validate one agent
    python scripts/validate_specs.py --skill STAGE  # validate one skill
    python scripts/validate_specs.py --cross-link-only  # skip per-spec, run only cross-link
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from research_pipeline.paths import REPO_ROOT
from research_pipeline.tools import spec_io

REPO = REPO_ROOT


def _print_banner(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
def _print_spec_result(label: str, result: dict[str, Any]) -> bool:
    status = result.get("status", "?")
    errors = result.get("errors") or []
    icon = "PASS" if status == "pass" else "FAIL"
    print(f"  [{icon}] {label}")
    for err in errors[:5]:
        print(f"        - {err}")
    if len(errors) > 5:
        print(f"        - ... ({len(errors) - 5} more)")
    return bool(status == "pass")


def validate_all_agents(strict: bool = False) -> tuple[int, int]:
    """Validate every .claude/agents/<name>.json. Returns (passed, total)."""
    agents = spec_io.list_agents()
    if not agents:
        print("  (no agent specs found in .claude/agents/)")
        return 0, 0

    passed, total = 0, 0
    for name in agents:
        total += 1
        try:
            spec = spec_io.load_agent_spec(name)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"  [FAIL] {name}: load error: {exc}")
            continue
        result = spec_io.validate_agent_spec(spec)
        if _print_spec_result(f"agent/{name}", result):
            passed += 1
    return passed, total


def validate_all_skills(strict: bool = False) -> tuple[int, int]:
    """Validate every .claude/skills/<stage>/skill.json. Returns (passed, total)."""
    skills = spec_io.list_skills()
    if not skills:
        print("  (no skill specs found in .claude/skills/)")
        return 0, 0

    passed, total = 0, 0
    for stage_id in skills:
        total += 1
        try:
            spec = spec_io.load_skill_spec(stage_id)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"  [FAIL] {stage_id}: load error: {exc}")
            continue
        result = spec_io.validate_skill_spec(spec)
        if _print_spec_result(f"skill/{stage_id}", result):
            passed += 1
    return passed, total


def validate_skill_helper_paths() -> bool:
    """Check that all helper paths defined in skill specs exist on disk."""
    skills = spec_io.list_skills()
    all_ok = True
    for stage_id in skills:
        try:
            spec = spec_io.load_skill_spec(stage_id)
        except Exception:
            continue
        helpers = spec.get("helpers", {})
        for name, path_str in helpers.items():
            path = REPO / path_str
            if not path.exists():
                print(f"  [FAIL] skill/{stage_id} helper '{name}' path '{path_str}' does not exist")
                all_ok = False
    if all_ok:
        print("  [PASS] All skill spec helper paths exist on disk")
    return all_ok


def validate_pipeline_schemas() -> bool:
    """Check that all schema files defined in pipeline.json exist."""
    pipeline_file = REPO / "pipeline.json"
    if not pipeline_file.exists():
        print("  [FAIL] pipeline.json is missing")
        return False
    try:
        cfg = json.loads(pipeline_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  [FAIL] pipeline.json load error: {exc}")
        return False

    all_ok = True
    stages = cfg.get("stages", [])
    for idx, stage in enumerate(stages):
        sid = stage.get("id", f"stage_{idx}")
        schema_path_str = stage.get("schema")
        if not schema_path_str:
            print(f"  [FAIL] pipeline stage '{sid}' is missing 'schema' property")
            all_ok = False
            continue
        path = REPO / schema_path_str
        if not path.exists():
            print(f"  [FAIL] pipeline stage '{sid}' schema path '{schema_path_str}' does not exist")
            all_ok = False

    if all_ok:
        print("  [PASS] All pipeline stage schema files exist on disk")
    return all_ok


def run_cross_link(strict: bool = False) -> bool:
    """Run cross-link check. Returns True if clean."""
    result = spec_io.cross_link_check()
    status = result.get("status", "?")
    issues = result.get("issues") or []
    icon = "PASS" if status in ("pass", "ok") else "FAIL"
    print(f"  [{icon}] cross_link_check: status={status}, issues={len(issues)}")
    for issue in issues[:10]:
        print(f"        - {issue}")
    if len(issues) > 10:
        print(f"        - ... ({len(issues) - 10} more)")
    return status in ("pass", "ok")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--agent", metavar="NAME", help="Validate a single agent by name")
    parser.add_argument("--skill", metavar="STAGE", help="Validate a single skill by stage id")
    parser.add_argument("--cross-link-only", action="store_true", help="Run only the cross-link check")
    args = parser.parse_args(argv)

    overall_ok = True

    if not args.cross_link_only and not args.skill:
        _print_banner("Agent specs (8 expected)")
        if args.agent:
            try:
                spec = spec_io.load_agent_spec(args.agent)
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                print(f"  [FAIL] {args.agent}: load error: {exc}")
                overall_ok = False
            else:
                if not _print_spec_result(f"agent/{args.agent}", spec_io.validate_agent_spec(spec)):
                    overall_ok = False
        else:
            passed, total = validate_all_agents(args.strict)
            print(f"\n  agent summary: {passed}/{total} pass")
            if passed != total:
                overall_ok = False

    if not args.cross_link_only and not args.agent:
        _print_banner("Skill specs (7 expected)")
        if args.skill:
            try:
                spec = spec_io.load_skill_spec(args.skill)
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                print(f"  [FAIL] {args.skill}: load error: {exc}")
                overall_ok = False
            else:
                if not _print_spec_result(f"skill/{args.skill}", spec_io.validate_skill_spec(spec)):
                    overall_ok = False
        else:
            passed, total = validate_all_skills(args.strict)
            print(f"\n  skill summary: {passed}/{total} pass")
            if passed != total:
                overall_ok = False

    _print_banner("Helper paths & Pipeline schemas validation")
    if not validate_skill_helper_paths():
        overall_ok = False
    if not validate_pipeline_schemas():
        overall_ok = False

    _print_banner("Cross-link check")
    if not run_cross_link(args.strict):
        overall_ok = False

    _print_banner("Result")
    if overall_ok:
        print("  ALL VALIDATIONS PASSED")
        return 0
    print("  VALIDATION FAILURES PRESENT — see above")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
