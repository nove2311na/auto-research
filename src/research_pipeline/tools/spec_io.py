"""spec_io.py — Draft-7 read/write/validate for .claude/ agents and skills.

Per .claude/rules/python.md:
  - Type hints on all signatures
  - pathlib.Path
  - logging, not print
  - Standard lib, then third-party, then local
"""
from __future__ import annotations

import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft7Validator

from research_pipeline.paths import CLAUDE_AGENTS, CLAUDE_SKILLS, REPO_ROOT, SCHEMAS

REPO = REPO_ROOT
AGENTS_DIR = CLAUDE_AGENTS
SKILLS_DIR = CLAUDE_SKILLS
SCHEMAS_DIR = SCHEMAS

logger = logging.getLogger("research_pipeline.tools.spec_io")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@lru_cache(maxsize=4)
def _load_schema(name: str) -> dict[str, Any]:
    """Load and cache a JSON Schema file from schemas/."""
    path = SCHEMAS_DIR / name
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _agent_json_path(name: str) -> Path:
    return AGENTS_DIR / f"{name}.json"


def _skill_json_path(stage_id: str) -> Path:
    return SKILLS_DIR / stage_id / "skill.json"


def _validate(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Run Draft7Validator; return {status, errors}."""
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(spec), key=lambda e: list(e.absolute_path))
    if not errors:
        return {"status": "pass", "errors": []}
    return {
        "status": "fail",
        "errors": [
            f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
            for err in errors[:20]
        ],
    }


def load_agent_spec(name: str) -> dict[str, Any]:
    """Load an agent spec by name (no extension). Reads <name>.json."""
    path = _agent_json_path(name)
    if not path.exists():
        raise FileNotFoundError(f"agent spec not found: {path}")
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def load_skill_spec(stage_id: str) -> dict[str, Any]:
    """Load a skill spec by stage id (e.g. '00_research'). Reads <stage_id>/skill.json."""
    path = _skill_json_path(stage_id)
    if not path.exists():
        raise FileNotFoundError(f"skill spec not found: {path}")
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def write_agent_spec(name: str, spec: dict[str, Any]) -> Path:
    """Validate-then-write an agent spec to .claude/agents/<name>.json (atomic via tools.artifact_io)."""
    from research_pipeline.tools.artifact_io import atomic_write
    result = validate_agent_spec(spec)
    if result["status"] != "pass":
        raise ValueError(f"agent spec invalid: {result['errors']}")
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    path = _agent_json_path(name)
    atomic_write(path, json.dumps(spec, indent=2, ensure_ascii=False))
    return path


def write_skill_spec(stage_id: str, spec: dict[str, Any]) -> Path:
    """Validate-then-write a skill spec to .claude/skills/<stage_id>/skill.json (atomic)."""
    from research_pipeline.tools.artifact_io import atomic_write
    result = validate_skill_spec(spec)
    if result["status"] != "pass":
        raise ValueError(f"skill spec invalid: {result['errors']}")
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    skill_dir = SKILLS_DIR / stage_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = _skill_json_path(stage_id)
    atomic_write(path, json.dumps(spec, indent=2, ensure_ascii=False))
    return path


def validate_agent_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate a dict against schemas/agent-spec.json (Draft-7)."""
    return _validate(spec, _load_schema("agent-spec.json"))


def validate_skill_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate a dict against schemas/skill-spec.json (Draft-7)."""
    return _validate(spec, _load_schema("skill-spec.json"))


def list_agents() -> list[str]:
    """Return sorted list of agent names with a <name>.json on disk."""
    if not AGENTS_DIR.exists():
        return []
    return sorted(p.stem for p in AGENTS_DIR.glob("*.json"))


def list_skills() -> list[str]:
    """Return sorted list of stage ids with a <stage_id>/skill.json on disk."""
    if not SKILLS_DIR.exists():
        return []
    out: list[str] = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and (d / "skill.json").exists():
            out.append(d.name)
    return out


def cross_link_check() -> dict[str, Any]:
    """Verify every agent's skills_owned ref exists and every skill's owning_agent ref exists."""
    issues: list[str] = []
    agents = {a["name"]: a for a in (load_agent_spec(n) for n in list_agents())}
    skills = {s["stage_id"]: s for s in (load_skill_spec(sid) for sid in list_skills())}

    if not agents and not skills:
        return {"status": "pass", "issues": ["no specs on disk (fresh repo)"]}

    for name, agent in agents.items():
        for ref in agent.get("skills_owned", []):
            target = ref.removesuffix(".md").replace("skills/", "", 1).replace("-", "_")
            if target not in skills:
                issues.append(f"agent '{name}' references skill '{ref}' (MISSING)")

    for stage_id, skill in skills.items():
        owner = skill.get("owning_agent")
        if owner and owner not in agents:
            issues.append(f"skill '{stage_id}' references agent '{owner}' (MISSING)")

    if issues:
        return {"status": "fail", "issues": issues}
    return {"status": "pass", "issues": ["all cross-links resolved"]}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    cmd = args[0]
    if cmd == "list-agents":
        for name in list_agents():
            print(name)
        return 0
    if cmd == "list-skills":
        for stage in list_skills():
            print(stage)
        return 0
    if cmd == "validate-agent":
        if len(args) < 2:
            print("Usage: python -m tools.spec_io validate-agent <name>")
            return 2
        result = validate_agent_spec(load_agent_spec(args[1]))
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    if cmd == "validate-skill":
        if len(args) < 2:
            print("Usage: python -m tools.spec_io validate-skill <stage_id>")
            return 2
        result = validate_skill_spec(load_skill_spec(args[1]))
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    if cmd == "cross-link":
        result = cross_link_check()
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    print(f"unknown cmd: {cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
