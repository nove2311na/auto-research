"""fetch_input.py — turn any input source into normalized plain text.

Supported input types:
  - text   (raw string)
  - file   (.txt / .md → read directly)
  - url    (HTTP GET + html2text)
  - pdf    (pypdf)
  - docx   (python-docx)
  - batch_dir  (a directory of files; returns a list of inputs)

Returns a (text, metadata) tuple. The Ingestor agent writes these to
outputs/<input_id>/01_ingest/v1.txt + v1.meta.json (via artifact_io).

Usage:
    from tools.fetch_input import fetch
    text, meta = fetch("inputs/inbox/note.txt")
"""
from __future__ import annotations
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
INBOX = REPO / "inputs" / "inbox"


def _is_url(s: str) -> bool:
    try:
        u = urlparse(s)
        return u.scheme in ("http", "https") and bool(u.netloc)
    except Exception:
        return False


def _read_text_file(p: Path) -> tuple[str, dict]:
    text = p.read_text(errors="replace")
    return text, {
        "source_type": "file",
        "source_ref": str(p),
        "size_bytes": p.stat().st_size,
        "encoding": "utf-8",
    }


def _read_url(url: str) -> tuple[str, dict]:
    import requests
    r = requests.get(url, timeout=30, headers={"User-Agent": "research-pipeline/1.0"})
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    body = r.text
    if "html" in ctype.lower():
        try:
            import html2text
            text = html2text.html2text(body)
        except ImportError:
            text = re.sub(r"<[^>]+>", "", body)
        # Try to extract <title>
        m = re.search(r"<title>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else ""
    else:
        text = body
        title = ""
    meta: dict[str, Any] = {
        "source_type": "url",
        "source_ref": url,
        "size_bytes": len(r.content),
        "encoding": r.encoding or "utf-8",
    }
    if title:
        meta["title"] = title
    return text, meta


def _read_pdf(p: Path) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("pypdf not installed; `uv add pypdf`")
    reader = PdfReader(str(p))
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    text = "\n\n".join(parts)
    meta: dict[str, Any] = {
        "source_type": "pdf",
        "source_ref": str(p),
        "size_bytes": p.stat().st_size,
        "title": (reader.metadata.title or "") if reader.metadata else "",
    }
    return text, meta


def _read_docx(p: Path) -> tuple[str, dict]:
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("python-docx not installed; `uv add python-docx`")
    doc = Document(str(p))
    text = "\n\n".join(par.text for par in doc.paragraphs if par.text)
    meta: dict[str, Any] = {
        "source_type": "docx",
        "source_ref": str(p),
        "size_bytes": p.stat().st_size,
        "title": (doc.core_properties.title or "") if doc.core_properties else "",
    }
    return text, meta


def fetch(source: str | Path) -> tuple[str, dict]:
    """Return (text, metadata). `source` can be a path, URL, or raw text."""
    if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        p = Path(source)
        suffix = p.suffix.lower()
        if suffix in (".txt", ".md", ".markdown", ".rst"):
            return _read_text_file(p)
        if suffix == ".pdf":
            return _read_pdf(p)
        if suffix in (".docx",):
            return _read_docx(p)
        # .url: read URL inside
        if suffix == ".url":
            url = p.read_text().strip()
            return _read_url(url)
        # Default: try as text
        return _read_text_file(p)
    if isinstance(source, str) and _is_url(source.strip()):
        return _read_url(source.strip())
    # Treat as raw text
    return source, {
        "source_type": "text",
        "source_ref": "inline",
        "size_bytes": len(source.encode("utf-8")),
        "encoding": "utf-8",
    }


def input_id_for(text: str) -> str:
    """Stable id derived from sha256 of the text content (first 8 hex)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def scan_inbox() -> list[Path]:
    """Return all files currently in inputs/inbox/."""
    if not INBOX.exists():
        return []
    return sorted([p for p in INBOX.iterdir() if p.is_file()])


def move_to_processed(p: Path) -> Path:
    """Move a file from inputs/inbox/ to inputs/processed/."""
    dst = REPO / "inputs" / "processed" / p.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        # Add suffix to avoid clobber
        i = 1
        while True:
            candidate = dst.with_name(f"{dst.stem}-{i}{dst.suffix}")
            if not candidate.exists():
                dst = candidate
                break
            i += 1
    p.rename(dst)
    return dst


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m tools.fetch_input <path-or-url>")
        sys.exit(1)
    text, meta = fetch(sys.argv[1])
    print(f"--- meta ---\n{meta}")
    print(f"--- text (first 500 chars) ---\n{text[:500]}")
