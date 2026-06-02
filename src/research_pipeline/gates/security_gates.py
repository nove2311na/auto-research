"""Security gates for static and dynamic checks."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


def _fail(summary: str, evidence: list[str], risks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"status": "fail", "summary": summary, "evidence": evidence, "risks": risks}


def path_safety_gate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate that files are safe and do not contain obvious keys/secrets."""
    ref = input_data.get("ref", "")
    evidence = [f"ref: {ref}"]

    # 1. Path traversal check
    if ref and ("../" in ref or "..\\" in ref):
        return _fail(
            "security gate failed: directory traversal pattern detected",
            evidence,
            [{"severity": "high", "description": "path traversal attempt", "required_fix": "remove relative traversal dots (../)"}],
        )

    if ref and os.path.exists(ref):
        try:
            # 2. File size check
            size = os.path.getsize(ref)
            evidence.append(f"size: {size} bytes")
            if size > 2 * 1024 * 1024:  # 2MB limit
                return _fail(
                    f"security gate failed: file size ({size} bytes) exceeds limit of 2MB",
                    evidence,
                    [{"severity": "medium", "description": "oversized input file", "required_fix": "reduce file size to less than 2MB"}],
                )

            content = Path(ref).read_text(encoding="utf-8", errors="ignore")

            # 3. Secret patterns check
            secret_patterns = [
                r"BEGIN [A-Z ]*PRIVATE KEY",
                r"aws_secret_access_key\s*[:=]",
                r"aws_access_key_id\s*[:=]",
                r"ghp_[A-Za-z0-9]{36,}",
                r"slack.com/services/T[A-Z0-9]{8}/",
                r"(api_key|secret_key|private_key|slack_token)\s*[:=]\s*[\"'][A-Za-z0-9_/+=.-]{16,}[\"']",
            ]

            for line_idx, line in enumerate(content.splitlines(), 1):
                for pattern in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        masked_line = line[:10] + "..." + line[-10:] if len(line) > 20 else "..."
                        return _fail(
                            f"security gate failed: secret or credential pattern detected on line {line_idx}",
                            evidence + [f"line {line_idx}: {masked_line}"],
                            [{"severity": "high", "description": "credential leakage", "required_fix": "revoke credentials and clean file"}],
                        )
        except Exception as e:
            evidence.append(f"Read error: {e}")

    return {
        "status": "pass",
        "summary": "security gate passed",
        "evidence": evidence,
        "risks": [],
    }
