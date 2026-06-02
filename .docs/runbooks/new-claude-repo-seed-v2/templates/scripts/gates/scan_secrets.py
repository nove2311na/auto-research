#!/usr/bin/env python3
"""Scan a repo for common committed-secret patterns."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{20,}"),
]


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in iter_files(root):
        text = read_text(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(str(path.relative_to(root)))
                break
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Repo root to scan")
    args = parser.parse_args(argv)

    findings = scan(Path(args.target).resolve())
    if findings:
        print("secret scan: fail")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("secret scan: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

