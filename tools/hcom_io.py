"""hcom_io.py — shared hcom send/list/bundle wrappers.

Used by all 7 agents. Importable from anywhere in the workspace.
Never blocks the caller; wraps hcom CLI calls with retry + timeout.

Usage:
    from tools.hcom_io import send, list_active, wait_for_message
    send("@runner", title="run", description="...", files=["./train.py"])
    agents = list_active()
"""
from __future__ import annotations
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterable

HCOM = shutil.which("hcom") or "hcom"
RETRY_BACKOFF_S = 2
MAX_RETRIES = 3


def _run(args: list[str], timeout: int = 30) -> str:
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
            err = r.stderr.strip() or r.stdout.strip()
        except subprocess.TimeoutExpired:
            err = f"timeout after {timeout}s"
        time.sleep(RETRY_BACKOFF_S * (attempt + 1))
    raise RuntimeError(f"hcom {args[0]} failed after {MAX_RETRIES} attempts: {err}")


def send(target: str, *, title: str, description: str,
         files: Iterable[str] = (),
         events: Iterable[str] = (),
         transcript: str | None = None) -> str:
    """Send a message to one agent. target like '@runner' or '@autoresearch-claude-5'."""
    args = ["send", target, "--",
            "--title", title,
            "--description", description]
    file_list = [f for f in files if Path(f).exists()]
    if file_list:
        args.extend(["--files", ",".join(file_list)])
    if events:
        args.extend(["--events", ",".join(events)])
    if transcript:
        args.extend(["--transcript", transcript])
    return _run(args)


def list_active() -> list[dict]:
    """Return JSON list of active agents."""
    out = _run(["list", "--json"])
    return json.loads(out) if out else []


def events(last: int = 20, collision: bool = False) -> list[dict]:
    """Return the last N events as JSON."""
    args = ["events", "--last", str(last), "--json"]
    if collision:
        args.append("--collision")
    out = _run(args)
    return json.loads(out) if out else []


def bundle_prepare() -> str:
    """Return the recommended bundle create command for the current session."""
    return _run(["bundle", "prepare", "--for", "self"])


def wait_for_message(timeout_s: int = 300) -> dict | None:
    """Block until a message arrives (or timeout). Returns the event dict or None."""
    out = _run(["listen", str(timeout_s)], timeout=timeout_s + 10)
    if not out:
        return None
    try:
        return json.loads(out)
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
