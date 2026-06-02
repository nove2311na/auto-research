#!/usr/bin/env python3
"""Initialize the MAS workspace without overwriting existing state."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_DIR = Path(__file__).resolve().parents[1] / "workspace"


def write_json_if_missing(path: Path, payload: Any) -> bool:
    """Write JSON only when the file does not already exist."""
    if path.exists():
        return False
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return True


def initialize_workspace(project: str, figma: str) -> list[str]:
    """Create workspace directories and seed files."""
    actions: list[str] = []
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    actions.append("workspace root ready")

    for directory in ("blueprints", "contents", "rawdata"):
        path = WORKSPACE_DIR / directory
        if path.exists():
            actions.append(f"kept workspace/{directory}/")
        else:
            path.mkdir(parents=True)
            actions.append(f"created workspace/{directory}/")

    initial_files: dict[str, Any] = {
        "meta.json": {
            "projectName": project,
            "figmaUrl": figma,
            "initializedAt": datetime.now(timezone.utc).isoformat(),
            "runtime": "claude_code_python",
        },
        "page_structure.json": [],
        "state.json": [],
        "error-logs.json": [],
        "design-system.json": {
            "variables": [],
            "global_classes": [],
            "client_first_library": "knowledge-base/client-first-class-map.json",
            "figma_mapping_contract": "agentic/specs/figma-to-client-first-mapping.md",
        },
    }

    for filename, payload in initial_files.items():
        created = write_json_if_missing(WORKSPACE_DIR / filename, payload)
        actions.append(f"{'created' if created else 'kept'} workspace/{filename}")

    return actions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="New Project", help="Project name")
    parser.add_argument("--figma", default="", help="Figma design URL")
    args = parser.parse_args(argv)

    for action in initialize_workspace(args.project, args.figma):
        print(action)
    print("workspace ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
