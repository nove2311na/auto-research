#!/usr/bin/env python3
"""memory_retriever.py — Retrieve matching past lessons based on keywords/topics.

Usage:
    python -m research_pipeline.tools.memory_retriever <keyword>
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LEARNINGS_FILE = REPO_ROOT / "learnings.md"
ARCHIVE_DIR = REPO_ROOT / "learnings.archive"


def retrieve_learnings(keyword: str) -> list[str]:
    results = []
    kw_lower = keyword.lower()
    
    # Check active learnings
    if LEARNINGS_FILE.exists():
        content = LEARNINGS_FILE.read_text(encoding="utf-8")
        # Split by ## headers
        entries = content.split("## ")
        for entry in entries:
            if kw_lower in entry.lower():
                results.append("## " + entry.strip())
                
    # Check archived learnings
    if ARCHIVE_DIR.exists():
        for archive in ARCHIVE_DIR.glob("*.md"):
            content = archive.read_text(encoding="utf-8")
            entries = content.split("## ")
            for entry in entries:
                if kw_lower in entry.lower():
                    results.append(f"## [ARCHIVED: {archive.name}] " + entry.strip())
                    
    return results


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m research_pipeline.tools.memory_retriever <keyword>")
        sys.exit(1)
        
    keyword = sys.argv[1]
    matches = retrieve_learnings(keyword)
    
    if not matches:
        print(f"No past lessons found matching '{keyword}'.")
        sys.exit(0)
        
    print(f"=== Found {len(matches)} past lessons matching '{keyword}' ===")
    for match in matches[:5]:  # Display top 5 matches
        print(match)
        print("-" * 40)


if __name__ == "__main__":
    main()
