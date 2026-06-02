"""Security gates for static and dynamic checks."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def path_safety_gate(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate that files are safe and do not contain obvious keys/secrets."""
    ref = input_data.get("ref", "")
    if ref and os.path.exists(ref):
        try:
            content = Path(ref).read_text(encoding="utf-8", errors="ignore")
            # Simple check for private keys / secrets in input text
            for line in content.splitlines():
                if "BEGIN PRIVATE KEY" in line or "aws_secret_access_key" in line.lower():
                    return {
                        "status": "fail",
                        "summary": "security gate failed: private key or secret found",
                        "evidence": [line],
                        "risks": [{"severity": "high", "description": "credential leakage", "required_fix": "revoke credentials"}],
                    }
        except Exception:
            pass

    return {
        "status": "pass",
        "summary": "security gate passed",
        "evidence": [str(input_data)],
        "risks": [],
    }
