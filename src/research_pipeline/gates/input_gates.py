"""Input gates that run before the orchestrator accepts an input."""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

MAX_INPUT_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


def _ok(summary: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": "pass", "summary": summary, "evidence": evidence or [], "risks": []}


def _fail(summary: str, evidence: list[str], risks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": "fail", "summary": summary, "evidence": evidence, "risks": risks}


def _is_url(s: str) -> bool:
    try:
        u = urlparse(s)
        return u.scheme in ("http", "https") and bool(u.netloc)
    except Exception:
        return False


def completeness_gate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate raw user input (e.g. non-empty, path exists, safe file size, URL responsiveness)."""
    ref = input_data.get("ref", "")
    if not ref:
        return _fail(
            "missing 'ref' parameter",
            [],
            [{"severity": "high", "description": "no input reference provided", "required_fix": "provide 'ref' field"}]
        )

    evidence = [f"ref: {ref}"]

    if _is_url(ref):
        # 1. URL branch check
        import requests
        try:
            # Probe with HEAD first
            r = requests.head(ref, timeout=3, allow_redirects=True)
            if r.status_code >= 400:
                # Retry with GET as some servers block HEAD
                r = requests.get(ref, timeout=3, allow_redirects=True, stream=True)

            if r.status_code >= 400:
                return _fail(
                    f"URL probe failed with HTTP status code {r.status_code} for URL: {ref}",
                    evidence,
                    [{"severity": "high", "description": "unreachable URL", "required_fix": "verify URL is active and public"}]
                )

            # 2. Check content size from Content-Length header
            cl_str = r.headers.get("content-length")
            if cl_str:
                try:
                    size = int(cl_str)
                    evidence.append(f"Content-Length: {size} bytes")
                    if size > MAX_INPUT_SIZE_BYTES:
                        return _fail(
                            f"URL content size ({size} bytes) exceeds the limit of {MAX_INPUT_SIZE_BYTES} bytes.",
                            evidence,
                            [{"severity": "high", "description": "URL content is too large", "required_fix": "provide a smaller input source"}]
                        )
                except ValueError:
                    pass
        except Exception as e:
            return _fail(
                f"URL probe failed to connect or timed out: {e}",
                evidence,
                [{"severity": "high", "description": "URL connection timeout/error", "required_fix": "check network or URL validity"}]
            )

        return _ok(f"input URL verified and responsive: {ref}", evidence)

    else:
        # Local file branch
        if not os.path.exists(ref):
            return _fail(
                f"input ref not found on disk: {ref}",
                evidence,
                [{"severity": "high", "description": "local file not found", "required_fix": "check file path"}]
            )

        # Check file size limit
        try:
            size = os.path.getsize(ref)
            evidence.append(f"File size: {size} bytes")
            if size > MAX_INPUT_SIZE_BYTES:
                return _fail(
                    f"Local file size ({size} bytes) exceeds the limit of {MAX_INPUT_SIZE_BYTES} bytes.",
                    evidence,
                    [{"severity": "high", "description": "file is too large", "required_fix": "provide a file smaller than 5MB"}]
                )
        except Exception as e:
            return _fail(
                f"Failed to read file size: {e}",
                evidence,
                [{"severity": "medium", "description": "unreadable file metadata", "required_fix": "check file permissions"}]
            )

        return _ok(f"input file verified: {ref}", evidence)
