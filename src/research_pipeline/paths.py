"""Central filesystem paths for the research pipeline.

Keep runtime and contract paths anchored at the repository root even when
implementation modules live under ``src/research_pipeline``.
"""
from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = SRC_ROOT.parent

PIPELINE_JSON = REPO_ROOT / "pipeline.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

CLAUDE_DIR = REPO_ROOT / ".claude"
CLAUDE_AGENTS = CLAUDE_DIR / "agents"
CLAUDE_SKILLS = CLAUDE_DIR / "skills"
HCOM_DIR = REPO_ROOT / ".hcom"

INPUTS = REPO_ROOT / "inputs"
INBOX = INPUTS / "inbox"
PROCESSED = INPUTS / "processed"
OUTPUTS = REPO_ROOT / "outputs"
SCHEMAS = REPO_ROOT / "schemas"
EVALS = REPO_ROOT / "evals"
OBSERVABILITY = REPO_ROOT / "observability"


def repo_path(*parts: str) -> Path:
    """Return an absolute path inside the repository root."""
    return REPO_ROOT.joinpath(*parts)

