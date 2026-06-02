"""hcom_io.py — shared hcom send/list/bundle wrappers.

Used by all 8 agents. Importable from anywhere in the workspace.
Never blocks the caller; wraps hcom CLI calls with retry + timeout.

Usage:
    from research_pipeline.tools.hcom_io import send, list_active, wait_for_message
    send("@runner", title="run", description="...", files=["./train.py"])
    agents = list_active()
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

HCOM = shutil.which("hcom") or "hcom"
RETRY_BACKOFF_S = 2
MAX_RETRIES = 3
WINDOWS_POST_SEND_ERROR = "PTY wrapper requires Unix-only APIs"


def _identity_args() -> list[str]:
    """Return hcom identity flags for the current process.

    hcom v0.6.x on Windows is strict about identities for non-interactive
    commands. Launched agents get HCOM_NAME from scripts/launch.py; local
    kickoff scripts use bigboss.
    """
    name = (
        os.environ.get("HCOM_NAME")
        or os.environ.get("HCOM_INSTANCE_NAME")
        or os.environ.get("HCOM_SENDER")
        or os.environ.get("HCOM_NAME_OVERRIDE")
        or "bigboss"
    )
    return ["--name", name]


def _format_message(target: str, title: str, description: str, files: list[str]) -> str:
    title = title.replace("@", "[at]")
    description = description.replace("@", "[at]")
    message = f"{target} {title}\n\n{description}".strip()
    if files:
        message += "\n\nFiles:\n" + "\n".join(f"- {f}" for f in files)
    return message


def _run(args: list[str], timeout: int = 30) -> str:
    err = ""
    for attempt in range(MAX_RETRIES):
        try:
            r = subprocess.run(
                [HCOM, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if r.returncode == 0:
                return r.stdout.strip()
            if WINDOWS_POST_SEND_ERROR in f"{r.stderr}\n{r.stdout}":
                return r.stdout.strip()
            err = r.stderr.strip() or r.stdout.strip()
        except subprocess.TimeoutExpired:
            err = f"timeout after {timeout}s"
        time.sleep(RETRY_BACKOFF_S * (attempt + 1))
    raise RuntimeError(f"hcom {args[0]} failed after {MAX_RETRIES} attempts: {err}")


def _loads_ndjson(out: str) -> list[dict[str, Any]]:
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        rows.append(cast(dict[str, Any], json.loads(line)))
    return rows


def send(target: str, *, title: str, description: str,
         files: Iterable[str] = (),
         events: Iterable[str] = (),
         transcript: str | None = None) -> str:
    """Send a message to one agent. target like '@runner' or '@autoresearch-claude-5'."""
    file_list = [f for f in files if Path(f).exists()]
    context_lines = []
    if events:
        context_lines.append("Events: " + ", ".join(events))
    if transcript:
        context_lines.append(f"Transcript: {transcript}")
    if context_lines:
        description = f"{description}\n\n" + "\n".join(context_lines)

    message = _format_message(target, title, description, file_list)
    args = ["send", *_identity_args(), "--stdin"]
    return _run_with_stdin(args, message)


def _run_with_stdin(args: list[str], stdin: str, timeout: int = 30) -> str:
    err = ""
    for attempt in range(MAX_RETRIES):
        try:
            r = subprocess.run(
                [HCOM, *args],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if r.returncode == 0:
                return r.stdout.strip()
            if WINDOWS_POST_SEND_ERROR in f"{r.stderr}\n{r.stdout}":
                return r.stdout.strip()
            err = r.stderr.strip() or r.stdout.strip()
        except subprocess.TimeoutExpired:
            err = f"timeout after {timeout}s"
        time.sleep(RETRY_BACKOFF_S * (attempt + 1))
    raise RuntimeError(f"hcom {args[0]} failed after {MAX_RETRIES} attempts: {err}")


def list_active() -> list[dict[str, Any]]:
    """Return JSON list of active agents."""
    out = _run(["list", *_identity_args(), "--json"])
    if not out:
        return []
    rows = _loads_ndjson(out)
    return [row for row in rows if "_self" not in row]


def events(last: int = 20, collision: bool = False) -> list[dict[str, Any]]:
    """Return the last N events as JSON."""
    args = ["events", *_identity_args(), "--last", str(last), "--json"]
    if collision:
        args.append("--collision")
    out = _run(args)
    return _loads_ndjson(out) if out else []


def bundle_prepare() -> str:
    """Return the recommended bundle create command for the current session."""
    return _run(["bundle", "prepare", *_identity_args(), "--for", "self"])


def wait_for_message(timeout_s: int = 300) -> dict[str, Any] | None:
    """Block until a message arrives (or timeout). Returns the event dict or None."""
    out = _run(["listen", *_identity_args(), str(timeout_s)], timeout=timeout_s + 10)
    if not out:
        return None
    try:
        return cast(dict[str, Any], json.loads(out))
    except json.JSONDecodeError:
        return {"raw": out}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m tools.hcom_io <list|events|wait> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        print(json.dumps(list_active(), indent=2))
    elif cmd == "events":
        print(json.dumps(events(), indent=2))
    elif cmd == "wait":
        print(json.dumps(wait_for_message(), indent=2))
